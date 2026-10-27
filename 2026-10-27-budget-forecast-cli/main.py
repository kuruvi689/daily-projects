import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a simple 3‑month budget forecast based on past expenses."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to CSV file with historic expenses. Required columns: date, amount, category",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("forecast.json"),
        help="File to write the JSON forecast (default: forecast.json)",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=3,
        help="Number of future months to forecast (default: 3)",
    )
    return parser.parse_args()

def load_expenses(csv_path: Path):
    expenses = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"date", "amount", "category"}
        if not required.issubset(reader.fieldnames or []):
            sys.exit("CSV must contain columns: date, amount, category")
        for row in reader:
            try:
                date = datetime.strptime(row["date"], "%Y-%m-%d").date()
                amount = float(row["amount"])
                category = row["category"].strip()
                expenses.append({"date": date, "amount": amount, "category": category})
            except Exception as e:
                sys.exit(f"Error parsing row {row}: {e}")
    return expenses

def aggregate_monthly(expenses):
    monthly = defaultdict(lambda: defaultdict(float))
    for e in expenses:
        month = e["date"].replace(day=1)
        monthly[month][e["category"]] += e["amount"]
    return monthly

def average_monthly_spend(monthly, months=3):
    # Compute average spend per category over the most recent *months* of data
    sorted_months = sorted(monthly.keys(), reverse=True)[:months]
    if not sorted_months:
        return {}
    totals = defaultdict(float)
    for m in sorted_months:
        for cat, amt in monthly[m].items():
            totals[cat] += amt
    avg = {cat: round(tot / len(sorted_months), 2) for cat, tot in totals.items()}
    return avg

def forecast(avg_spend, start_date, periods):
    forecasts = []
    cur = start_date.replace(day=1)
    for _ in range(periods):
        month_str = cur.strftime("%Y-%m")
        forecasts.append({"month": month_str, "forecast": avg_spend})
        # advance one month
        year = cur.year + (cur.month // 12)
        month = (cur.month % 12) + 1
        cur = cur.replace(year=year, month=month)
    return forecasts

def main():
    args = parse_args()
    expenses = load_expenses(args.input)
    if not expenses:
        sys.exit("No expense data found.")
    monthly = aggregate_monthly(expenses)
    avg_spend = average_monthly_spend(monthly, months=3)
    if not avg_spend:
        sys.exit("Unable to compute average spend – check your data.")
    # Forecast starts from next month after the latest expense month
    latest_month = max(monthly.keys())
    forecast_data = forecast(avg_spend, latest_month + timedelta(days=31), args.period)
    # Write JSON output
    args.output.write_text(json.dumps({"forecast": forecast_data}, indent=2), encoding="utf-8")
    print(f"Forecast written to {args.output}")

if __name__ == "__main__":
    main()
