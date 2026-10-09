import argparse
import csv
import datetime
import json
import sys
from collections import defaultdict
from pathlib import Path

def parse_timestamp(ts: str) -> datetime.datetime:
    # Accept ISO format or common formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.datetime.strptime(ts, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized timestamp format: {ts}")

def load_sessions(file_path: Path):
    sessions = []
    with file_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"start", "end", "project", "interruptions"}
        if not required.issubset(reader.fieldnames):
            missing = required - set(reader.fieldnames or [])
            raise ValueError(f"CSV missing required columns: {', '.join(missing)}")
        for row in reader:
            try:
                start = parse_timestamp(row["start"].strip())
                end = parse_timestamp(row["end"].strip())
                if end < start:
                    raise ValueError("end before start")
                duration = (end - start).total_seconds() / 60  # minutes
                interruptions = int(row["interruptions"].strip())
                sessions.append({
                    "project": row["project"].strip(),
                    "duration": duration,
                    "interruptions": interruptions,
                })
            except Exception as e:
                print(f"Skipping malformed row {reader.line_num}: {e}", file=sys.stderr)
    return sessions

def summarize(sessions):
    per_project = defaultdict(lambda: {"total_minutes": 0.0, "sessions": 0, "interruptions": 0})
    total_minutes = 0.0
    total_interruptions = 0
    for s in sessions:
        proj = s["project"]
        per_project[proj]["total_minutes"] += s["duration"]
        per_project[proj]["sessions"] += 1
        per_project[proj]["interruptions"] += s["interruptions"]
        total_minutes += s["duration"]
        total_interruptions += s["interruptions"]
    avg_session = total_minutes / len(sessions) if sessions else 0
    summary = {
        "overall": {
            "total_sessions": len(sessions),
            "total_minutes": round(total_minutes, 2),
            "average_session_minutes": round(avg_session, 2),
            "total_interruptions": total_interruptions,
        },
        "by_project": {},
    }
    for proj, data in per_project.items():
        summary["by_project"][proj] = {
            "sessions": data["sessions"],
            "total_minutes": round(data["total_minutes"], 2),
            "average_minutes": round(data["total_minutes"] / data["sessions"], 2),
            "interruptions": data["interruptions"],
        }
    return summary

def format_markdown(summary):
    lines = []
    lines.append("# Focus Session Analysis")
    lines.append("")
    overall = summary["overall"]
    lines.append("## Overall Summary")
    lines.append(f"- Total Sessions: {overall['total_sessions']}")
    lines.append(f"- Total Time: {overall['total_minutes']} minutes")
    lines.append(f"- Avg Session Length: {overall['average_session_minutes']} minutes")
    lines.append(f"- Total Interruptions: {overall['total_interruptions']}")
    lines.append("")
    lines.append("## By Project")
    for proj, data in summary["by_project"].items():
        lines.append(f"### {proj}")
        lines.append(f"- Sessions: {data['sessions']}")
        lines.append(f"- Total Time: {data['total_minutes']} minutes")
        lines.append(f"- Avg Session: {data['average_minutes']} minutes")
        lines.append(f"- Interruptions: {data['interruptions']}")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Analyze focus‑session logs and produce a markdown summary.")
    parser.add_argument("log", type=Path, help="Path to CSV log file. Columns: start,end,project,interruptions")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Write markdown to file (default: stdout)")
    args = parser.parse_args()
    try:
        sessions = load_sessions(args.log)
    except Exception as e:
        print(f"Error loading log: {e}", file=sys.stderr)
        sys.exit(1)
    if not sessions:
        print("No valid sessions found.", file=sys.stderr)
        sys.exit(1)
    summary = summarize(sessions)
    markdown = format_markdown(summary)
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Summary written to {args.output}")
    else:
        print(markdown)

if __name__ == "__main__":
    main()
