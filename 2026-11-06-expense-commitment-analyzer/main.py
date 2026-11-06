import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from statistics import mean, stdev

DEFAULT_CATEGORIES = {
    "food": ["grocery", "restaurant", "cafe", "dining"],
    "transport": ["uber", "taxi", "bus", "metro", "fuel", "gas"],
    "entertainment": ["movie", "netflix", "spotify", "gaming"],
    "shopping": ["clothing", "apparel", "shoes", "amazon", "store"],
    "bills": ["electricity", "water", "internet", "phone", "rent", "mortgage"],
    "health": ["pharmacy", "doctor", "hospital", "gym"],
    "others": []
}

def load_expenses(path):
    expenses = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Expected columns: date, description, amount, currency (optional)
            try:
                date = datetime.strptime(row["date"], "%Y-%m-%d")
            except Exception:
                print(f"Skipping row with invalid date: {row}", file=sys.stderr)
                continue
            amount = float(row["amount"])
            currency = row.get("currency", "USD").upper()
            desc = row["description"].lower()
            expenses.append({"date": date, "desc": desc, "amount": amount, "currency": currency})
    return expenses

def simple_category(desc):
    for cat, keywords in DEFAULT_CATEGORIES.items():
        for kw in keywords:
            if kw in desc:
                return cat
    return "others"

def aggregate_by_month(expenses):
    monthly = defaultdict(list)
    for e in expenses:
        key = e["date"].strftime("%Y-%m")
        monthly[key].append(e)
    return monthly

def flag_anomalies(monthly):
    # Compute average spend per category across all months
    cat_totals = defaultdict(list)
    for month, items in monthly.items():
        cat_sum = defaultdict(float)
        for e in items:
            cat = simple_category(e["desc"]) if not e.get("category") else e["category"]
            cat_sum[cat] += e["amount"]
        for cat, amt in cat_sum.items():
            cat_totals[cat].append(amt)
    cat_stats = {}
    for cat, values in cat_totals.items():
        avg = mean(values)
        sigma = stdev(values) if len(values) > 1 else 0
        cat_stats[cat] = (avg, sigma)
    # Flag months where spend > avg + 2*sd
    anomalies = []
    for month, items in monthly.items():
        cat_sum = defaultdict(float)
        for e in items:
            cat = simple_category(e["desc"]) if not e.get("category") else e["category"]
            cat_sum[cat] += e["amount"]
        for cat, amt in cat_sum.items():
            avg, sigma = cat_stats[cat]
            if sigma and amt > avg + 2 * sigma:
                anomalies.append({"month": month, "category": cat, "amount": amt, "avg": avg, "sd": sigma})
    return anomalies

def export_summary(monthly, anomalies, out_path):
    summary = []
    for month, items in sorted(monthly.items()):
        total = sum(e["amount"] for e in items)
        cat_breakdown = defaultdict(float)
        for e in items:
            cat = simple_category(e["desc"]) if not e.get("category") else e["category"]
            cat_breakdown[cat] += e["amount"]
        summary.append({
            "month": month,
            "total": round(total, 2),
            "breakdown": {k: round(v, 2) for k, v in cat_breakdown.items()}
        })
    report = {"summary": summary, "anomalies": anomalies}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report written to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Expense Commitment Analyzer – flag unusual spending and export a concise monthly report.")
    parser.add_argument("csv_path", help="Path to expenses CSV (date,description,amount,currency(optional))")
    parser.add_argument("--out", default="expense_report.json", help="Output JSON report file")
    args = parser.parse_args()

    if not os.path.isfile(args.csv_path):
        print(f"File not found: {args.csv_path}", file=sys.stderr)
        sys.exit(1)

    expenses = load_expenses(args.csv_path)
    if not expenses:
        print("No valid expense rows found.", file=sys.stderr)
        sys.exit(1)

    monthly = aggregate_by_month(expenses)
    anomalies = flag_anomalies(monthly)
    export_summary(monthly, anomalies, args.out)

if __name__ == "__main__":
    main()
