import csv
import json
import argparse
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter

def load_expenses(file_path: str):
    """Load expenses from a CSV file.
    Expected columns: date, amount, category, description (optional).
    Date format: YYYY-MM-DD
    """
    expenses = []
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    expense = {
                        "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                        "amount": float(row["amount"]),
                        "category": row["category"].strip().lower(),
                        "description": row.get("description", "").strip()
                    }
                    expenses.append(expense)
                except Exception as e:
                    print(f"Skipping row due to error: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    return expenses

def aggregate_monthly(expenses):
    """Return a dict mapping (year, month) -> total amount per category."""
    monthly = defaultdict(lambda: defaultdict(float))
    for exp in expenses:
        key = (exp["date"].year, exp["date"].month)
        monthly[key][exp["category"]] += exp["amount"]
    return monthly

def forecast_next_month(monthly):
    """Simple forecast: average of same month over past years.
    Returns dict of category -> forecasted amount.
    """
    # Gather data by month number across years
    month_data = defaultdict(list)  # month -> list of totals per year
    for (year, month), cat_totals in monthly.items():
        total = sum(cat_totals.values())
        month_data[month].append(total)
    forecast = {}
    for month, totals in month_data.items():
        if totals:
            forecast[month] = sum(totals) / len(totals)
    # Return forecast for next month based on current date
    next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1)
    return {"year": next_month.year, "month": next_month.month, "forecast": forecast.get(next_month.month, 0.0)}

def detect_anomalies(expenses, threshold=2.0):
    """Flag expenses that are > threshold * median for their category.
    Returns list of flagged expense dicts.
    """
    cat_amounts = defaultdict(list)
    for exp in expenses:
        cat_amounts[exp["category"]].append(exp["amount"])
    medians = {}
    for cat, amounts in cat_amounts.items():
        sorted_amt = sorted(amounts)
        n = len(sorted_amt)
        median = (sorted_amt[n // 2] if n % 2 else (sorted_amt[n // 2 - 1] + sorted_amt[n // 2]) / 2)
        medians[cat] = median
    flagged = []
    for exp in expenses:
        median = medians[exp["category"]]
        if median and exp["amount"] > threshold * median:
            flagged.append(exp)
    return flagged

def export_summary(monthly, forecast, flagged, output_path: str):
    summary = {
        "monthly_totals": {f"{year}-{month:02d}": dict(cat_totals) for (year, month), cat_totals in monthly.items()},
        "next_month_forecast": forecast,
        "anomalies": [
            {
                "date": exp["date"].strftime("%Y-%m-%d"),
                "category": exp["category"],
                "amount": exp["amount"],
                "description": exp["description"]
            }
            for exp in flagged
        ]
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Expense Forecast CLI – lightweight SaaS‑ready tool")
    parser.add_argument("csv_file", help="Path to expenses CSV file")
    parser.add_argument("--output", "-o", default="expense_summary.json", help="Output JSON summary file")
    parser.add_argument("--threshold", "-t", type=float, default=2.0, help="Anomaly detection multiplier (default 2.0)")
    args = parser.parse_args()

    expenses = load_expenses(args.csv_file)
    if not expenses:
        print("No expenses loaded – exiting.")
        sys.exit(0)

    monthly = aggregate_monthly(expenses)
    forecast = forecast_next_month(monthly)
    flagged = detect_anomalies(expenses, threshold=args.threshold)
    export_summary(monthly, forecast, flagged, args.output)

if __name__ == "__main__":
    main()
