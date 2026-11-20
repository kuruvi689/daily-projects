import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta

def parse_time(ts: str) -> datetime:
    # Accept ISO format or simple HH:MM
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognised time format: {ts}")

def load_sessions(path: str):
    sessions = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"start","end","project","interruptions"}
        if not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"CSV must contain columns: {', '.join(required)}")
        for row in reader:
            try:
                start = parse_time(row["start"].strip())
                end = parse_time(row["end"].strip())
                if end < start:
                    raise ValueError("end before start")
                duration = (end - start).total_seconds() / 60  # minutes
                interruptions = int(row["interruptions"].strip())
                project = row["project"].strip() or "unlabeled"
                sessions.append({
                    "start": start,
                    "end": end,
                    "project": project,
                    "duration": duration,
                    "interruptions": interruptions,
                })
            except Exception as e:
                print(f"Skipping malformed row {row}: {e}", file=sys.stderr)
    return sessions

def aggregate(sessions):
    stats = defaultdict(lambda: {"total_minutes": 0.0, "sessions": 0, "interruptions": 0})
    overall = {"total_minutes": 0.0, "sessions": 0, "interruptions": 0}
    for s in sessions:
        p = s["project"]
        stats[p]["total_minutes"] += s["duration"]
        stats[p]["sessions"] += 1
        stats[p]["interruptions"] += s["interruptions"]
        overall["total_minutes"] += s["duration"]
        overall["sessions"] += 1
        overall["interruptions"] += s["interruptions"]
    return stats, overall

def format_minutes(minutes: float) -> str:
    hrs = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hrs}h {mins}m" if hrs else f"{mins}m"

def report(stats, overall, json_out=None):
    lines = []
    lines.append("# Focus Session Analysis\n")
    lines.append(f"**Total Sessions:** {overall['sessions']}")
    lines.append(f"**Total Time:** {format_minutes(overall['total_minutes'])}")
    lines.append(f"**Total Interruptions:** {overall['interruptions']}\n")
    lines.append("## By Project\n")
    for proj, data in sorted(stats.items(), key=lambda x: -x[1]["total_minutes"]):
        avg_len = data["total_minutes"] / data["sessions"] if data["sessions"] else 0
        avg_int = data["interruptions"] / data["sessions"] if data["sessions"] else 0
        lines.append(f"### {proj}")
        lines.append(f"- Sessions: {data['sessions']}")
        lines.append(f"- Time: {format_minutes(data['total_minutes'])} (avg {format_minutes(avg_len)})")
        lines.append(f"- Interruptions: {data['interruptions']} (avg {avg_int:.1f})\n")
    output = "\n".join(lines)
    if json_out:
        payload = {"overall": overall, "by_project": stats}
        with open(json_out, "w", encoding="utf-8") as jf:
            json.dump(payload, jf, default=str, indent=2)
        print(f"JSON report written to {json_out}")
    print(output)

def main():
    parser = argparse.ArgumentParser(description="Analyze focus‑session logs and produce a concise report.")
    parser.add_argument("csv", help="Path to CSV log file. Columns: start,end,project,interruptions")
    parser.add_argument("-j", "--json", help="Optional path to write a detailed JSON report.")
    args = parser.parse_args()
    sessions = load_sessions(args.csv)
    if not sessions:
        print("No valid sessions found.")
        sys.exit(1)
    stats, overall = aggregate(sessions)
    report(stats, overall, json_out=args.json)

if __name__ == "__main__":
    main()
