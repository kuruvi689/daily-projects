import argparse
import csv
import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime

def load_expenses(file_path: str):
    """Load expenses from a CSV file.
    Expected columns: date, amount, category, description (optional)
    Date format: YYYY-MM-DD
    """
    expenses = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                expense = {
                    "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                    "amount": float(row["amount"]),
                    "category": row["category"].strip().lower() or "uncategorized",
                    "description": row.get("description", "").strip()
                }
                expenses.append(expense)
            except Exception as e:
                print(f"Skipping malformed row {row}: {e}", file=sys.stderr)
    return expenses

def group_by_month(expenses):
    groups = defaultdict(list)
    for exp in expenses:
        key = exp["date"].strftime("%Y-%m")
        groups[key].append(exp)
    return groups

def summarize_month(expenses):
    total = sum(e["amount"] for e in expenses)
    by_cat = Counter()
    for e in expenses:
        by_cat[e["category"]] += e["amount"]
    return total, by_cat

def detect_anomalies(expenses, threshold=2.0):
    """Flag expenses that are > threshold * median for their category.
    Returns list of anomalous expense dicts.
    """
    cat_values = defaultdict(list)
    for e in expenses:
        cat_values[e["category"]].append(e["amount"])
    anomalies = []
    for cat, amounts in cat_values.items():
        if len(amounts) < 3:
            continue
        median = sorted(amounts)[len(amounts)//2]
        for e in filter(lambda x: x["category"] == cat, expenses):
            if e["amount"] > median * threshold:
                anomalies.append(e)
    return anomalies

def export_summary(month, total, by_cat, anomalies, out_dir):
    summary = {
        "month": month,
        "total_spent": round(total, 2),
        "by_category": {cat: round(amt, 2) for cat, amt in by_cat.items()},
        "anomalies": [
            {
                "date": e["date"].strftime("%Y-%m-%d"),
                "amount": round(e["amount"], 2),
                "category": e["category"],
                "description": e["description"]
            }
            for e in anomalies if e["date"].strftime("%Y-%m") == month
        ]
    }
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{month}_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return out_path

def cli():
    parser = argparse.ArgumentParser(description="Expense Pattern Detector – group expenses, flag outliers, export monthly JSON summaries.")
    parser.add_argument("csv_file", help="Path to expenses CSV file")
    parser.add_argument("--out-dir", default="expense_reports", help="Directory to write monthly summaries")
    parser.add_argument("--threshold", type=float, default=2.0, help="Anomaly multiplier over median (default: 2.0)")
    args = parser.parse_args()

    if not os.path.isfile(args.csv_file):
        print(f"File not found: {args.csv_file}", file=sys.stderr)
        sys.exit(1)

    expenses = load_expenses(args.csv_file)
    if not expenses:
        print("No valid expense records loaded.", file=sys.stderr)
        sys.exit(1)

    months = group_by_month(expenses)
    anomalies = detect_anomalies(expenses, threshold=args.threshold)

    for month, month_exp in sorted(months.items()):
        total, by_cat = summarize_month(month_exp)
        out_path = export_summary(month, total, by_cat, anomalies, args.out_dir)
        print(f"✅ {month}: total ${total:.2f}, {len(by_cat)} categories → {out_path}")

if __name__ == "__main__":
    cli()
