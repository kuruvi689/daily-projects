import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect unusual expense patterns and generate a concise monthly report."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to CSV file containing expenses. Expected columns: date,amount,category,description",
    )
    parser.add_argument(
        "--output",
        default="expense_report.json",
        help="Path to JSON summary output (default: expense_report.json)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=2.0,
        help="Multiplier over average spend to flag an anomaly (default: 2.0)",
    )
    return parser.parse_args()

def load_expenses(csv_path):
    expenses = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                expense = {
                    "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                    "amount": float(row["amount"]),
                    "category": row["category"].strip().lower(),
                    "description": row.get("description", "").strip(),
                }
                expenses.append(expense)
            except Exception as e:
                print(f"Skipping malformed row {row}: {e}", file=sys.stderr)
    return expenses

def group_by_month(expenses):
    months = defaultdict(list)
    for exp in expenses:
        key = exp["date"].strftime("%Y-%m")
        months[key].append(exp)
    return months

def compute_monthly_stats(month_expenses, threshold):
    report = {}
    for month, items in month_expenses.items():
        total = sum(i["amount"] for i in items)
        count = len(items)
        avg = total / count if count else 0
        # Category breakdown
        cat_totals = defaultdict(float)
        for i in items:
            cat_totals[i["category"]] += i["amount"]
        # Detect anomalies: any expense > threshold * avg
        anomalies = [
            {
                "date": i["date"].strftime("%Y-%m-%d"),
                "amount": i["amount"],
                "category": i["category"],
                "description": i["description"],
            }
            for i in items
            if i["amount"] > threshold * avg and avg > 0
        ]
        report[month] = {
            "total_spent": round(total, 2),
            "average_spent": round(avg, 2),
            "transaction_count": count,
            "category_breakdown": {k: round(v, 2) for k, v in cat_totals.items()},
            "anomalies": anomalies,
        }
    return report

def generate_summary(report):
    summary = []
    for month in sorted(report.keys()):
        data = report[month]
        line = (
            f"{month}: total $ {data['total_spent']}, avg $ {data['average_spent']}, "
            f"{data['transaction_count']} transactions, "
            f"{len(data['anomalies'])} anomalies"
        )
        summary.append(line)
    return "\n".join(summary)

def main():
    args = parse_args()
    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    expenses = load_expenses(args.input)
    if not expenses:
        print("No valid expense records found.", file=sys.stderr)
        sys.exit(1)
    month_groups = group_by_month(expenses)
    report = compute_monthly_stats(month_groups, args.threshold)
    # Write detailed JSON report
    with open(args.output, "w", encoding="utf-8") as out:
        json.dump(report, out, indent=2, default=str)
    # Print concise human‑readable summary
    print("=== Expense Anomaly Summary ===")
    print(generate_summary(report))
    print(f"\nDetailed report written to {args.output}")

if __name__ == "__main__":
    main()
