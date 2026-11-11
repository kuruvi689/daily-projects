import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a performance dashboard for lead‑generation CSV data."
    )
    parser.add_argument(
        "input",
        help="Path to the lead‑gen CSV file. Expected columns: id, source, created_at, status, amount",
    )
    parser.add_argument(
        "--output",
        default="dashboard.json",
        help="Path to write the JSON summary (default: dashboard.json)",
    )
    parser.add_argument(
        "--date-format",
        default="%Y-%m-%d",
        help="Date format used in the CSV's created_at column (default: %%Y-%%m-%%d)",
    )
    return parser.parse_args()

def read_csv(path: str) -> List[Dict[str, str]]:
    if not os.path.isfile(path):
        sys.exit(f"Error: file not found – {path}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    if not rows:
        sys.exit("Error: CSV is empty or has no header.")
    return rows

def safe_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_date(value: str, fmt: str) -> datetime:
    try:
        return datetime.strptime(value, fmt)
    except (ValueError, TypeError):
        return None

def aggregate(rows: List[Dict[str, str]], date_fmt: str) -> Dict[str, Any]:
    total_leads = len(rows)
    status_counts = defaultdict(int)
    source_counts = defaultdict(int)
    amount_by_status = defaultdict(float)
    amount_by_source = defaultdict(float)
    created_dates: List[datetime] = []

    for r in rows:
        status = r.get("status", "unknown").strip().lower()
        source = r.get("source", "unknown").strip().lower()
        amount = safe_float(r.get("amount", "0"))
        created = safe_date(r.get("created_at", ""), date_fmt)

        status_counts[status] += 1
        source_counts[source] += 1
        amount_by_status[status] += amount
        amount_by_source[source] += amount
        if created:
            created_dates.append(created)

    # compute conversion rates (won vs total) if "won" status exists
    won = status_counts.get("won", 0)
    conversion_rate = round((won / total_leads) * 100, 2) if total_leads else 0.0

    # time‑range
    if created_dates:
        start_date = min(created_dates).date().isoformat()
        end_date = max(created_dates).date().isoformat()
    else:
        start_date = end_date = None

    summary = {
        "total_leads": total_leads,
        "date_range": {"start": start_date, "end": end_date},
        "status_breakdown": dict(status_counts),
        "source_breakdown": dict(source_counts),
        "amount_by_status": {k: round(v, 2) for k, v in amount_by_status.items()},
        "amount_by_source": {k: round(v, 2) for k, v in amount_by_source.items()},
        "conversion_rate_percent": conversion_rate,
    }
    return summary

def main() -> None:
    args = parse_args()
    rows = read_csv(args.input)
    dashboard = aggregate(rows, args.date_format)
    with open(args.output, "w", encoding="utf-8") as out:
        json.dump(dashboard, out, indent=2)
    print(f"Dashboard written to {args.output}")
    # pretty print to console for quick glance
    print(json.dumps(dashboard, indent=2))

if __name__ == "__main__":
    main()
