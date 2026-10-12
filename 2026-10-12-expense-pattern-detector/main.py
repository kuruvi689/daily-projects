import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime

def load_expenses(path):
    expenses = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row["amount"].replace(',', ''))
            except Exception:
                continue
            date_str = row.get("date", "")
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                date = None
            category = row.get("category", "Uncategorized").strip() or "Uncategorized"
            desc = row.get("description", "").strip()
            expenses.append({"date": date, "category": category, "amount": amount, "description": desc})
    return expenses

def group_by_category(expenses):
    groups = defaultdict(list)
    for e in expenses:
        groups[e["category"]].append(e)
    return groups

def stats_for_category(items):
    amounts = [e["amount"] for e in items]
    total = sum(amounts)
    avg = total / len(amounts) if amounts else 0
    var = sum((x - avg) ** 2 for x in amounts) / len(amounts) if amounts else 0
    std = math.sqrt(var)
    return {"total": total, "count": len(amounts), "avg": avg, "std": std}

def detect_anomalies(items, std_multiplier=2):
    stats = stats_for_category(items)
    threshold = stats["avg"] + std_multiplier * stats["std"]
    anomalies = [e for e in items if e["amount"] > threshold]
    return anomalies, threshold

def monthly_summary(expenses):
    summary = defaultdict(lambda: defaultdict(float))
    for e in expenses:
        if not e["date"]:
            continue
        month = e["date"].strftime("%Y-%m")
        summary[month][e["category"]] += e["amount"]
    return summary

def format_markdown(groups, anomalies_map, monthly):
    lines = ["# Expense Pattern Detector Summary", ""]
    lines.append("## Category Overview")
    for cat, items in groups.items():
        stats = stats_for_category(items)
        lines.append(f"- **{cat}**: {stats['count']} transactions, total ${stats['total']:.2f}, avg ${stats['avg']:.2f}")
    lines.append("")
    lines.append("## Anomalous Expenses ( > 2σ from mean )")
    any_anom = False
    for cat, (anoms, thr) in anomalies_map.items():
        if anoms:
            any_anom = True
            lines.append(f"### {cat} (threshold ${thr:.2f})")
            for a in anoms:
                date = a["date"].isoformat() if a["date"] else "?"
                lines.append(f"- {date}: ${a['amount']:.2f} – {a['description']}")
    if not any_anom:
        lines.append("No anomalies detected.")
    lines.append("")
    lines.append("## Monthly Spend Summary")
    for month in sorted(monthly.keys()):
        lines.append(f"### {month}")
        for cat, amt in monthly[month].items():
            lines.append(f"- {cat}: ${amt:.2f}")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Detect expense patterns and anomalies.")
    parser.add_argument("input", help="Path to CSV file with expenses. Columns: date,category,amount,description")
    parser.add_argument("-o", "--output", help="Path to write markdown report (default: stdout)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"Error: file not found – {args.input}")

    expenses = load_expenses(args.input)
    if not expenses:
        sys.exit("No valid expense records found.")

    groups = group_by_category(expenses)
    anomalies_map = {}
    for cat, items in groups.items():
        anoms, thr = detect_anomalies(items)
        anomalies_map[cat] = (anoms, thr)
    monthly = monthly_summary(expenses)
    report = format_markdown(groups, anomalies_map, monthly)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
