import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a concise daily/weekly summary of lead‑gen records for SaaS‑style reporting."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to CSV file containing raw lead‑gen rows. Expected columns: date,source,category,amount,status",
    )
    parser.add_argument(
        "--period",
        choices=["daily", "weekly", "monthly"],
        default="weekly",
        help="Aggregation period for the summary.",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="File to write JSON summary to. '-' writes to stdout.",
    )
    return parser.parse_args()


def read_csv(path: Path):
    if not path.is_file():
        sys.exit(f"Error: input file '{path}' not found.")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for i, row in enumerate(reader, start=2):
            try:
                row["date"] = datetime.strptime(row["date"].strip(), "%Y-%m-%d")
                row["amount"] = float(row["amount"].strip())
                rows.append(row)
            except Exception as e:
                sys.exit(f"Error parsing row {i}: {e}")
    return rows


def bucket_date(date: datetime, period: str):
    if period == "daily":
        return date.strftime("%Y-%m-%d")
    if period == "weekly":
        year, week, _ = date.isocalendar()
        return f"{year}-W{week:02d}"
    # monthly
    return date.strftime("%Y-%m")


def aggregate(rows, period):
    summary = defaultdict(lambda: {"leads": 0, "amount": 0.0, "by_source": defaultdict(int), "by_status": defaultdict(int)})
    for row in rows:
        bucket = bucket_date(row["date"], period)
        data = summary[bucket]
        data["leads"] += 1
        data["amount"] += row["amount"]
        data["by_source"][row["source"]] += 1
        data["by_status"][row["status"]] += 1
    # Convert inner defaultdicts to plain dicts for JSON serialisation
    for bucket, data in summary.items():
        data["by_source"] = dict(data["by_source"])
        data["by_status"] = dict(data["by_status"])
    return dict(summary)


def write_output(summary, out_path: str):
    json_str = json.dumps(summary, indent=2, sort_keys=True)
    if out_path == "-":
        print(json_str)
    else:
        Path(out_path).write_text(json_str, encoding="utf-8")
        print(f"Summary written to {out_path}")


def main():
    args = parse_args()
    rows = read_csv(Path(args.input))
    summary = aggregate(rows, args.period)
    write_output(summary, args.output)


if __name__ == "__main__":
    main()
