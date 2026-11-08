import argparse
import csv
import sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI tool to visualize expense trends over time. Reads a CSV of expenses and outputs monthly totals and an ASCII bar chart."
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to CSV file containing expenses. Expected columns: date, amount, category (optional).",
    )
    parser.add_argument(
        "-d",
        "--date-format",
        default="%Y-%m-%d",
        help="Date format used in the CSV (default: %%Y-%%m-%%d).",
    )
    parser.add_argument(
        "-c",
        "--currency",
        default="$",
        help="Currency symbol to display (default: $).",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=40,
        help="Maximum width of the ASCII bar chart (default: 40).",
    )
    return parser.parse_args()

def read_expenses(csv_path: Path, date_fmt: str) -> list[dict]:
    if not csv_path.is_file():
        sys.exit(f"Error: file not found – {csv_path}")
    expenses = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"date", "amount"}
        if not required.issubset(reader.fieldnames or []):
            sys.exit("Error: CSV must contain at least 'date' and 'amount' columns")
        for row in reader:
            try:
                date = datetime.strptime(row["date"].strip(), date_fmt)
                amount = float(row["amount"].strip())
            except Exception as e:
                sys.exit(f"Error parsing row {reader.line_num}: {e}")
            expenses.append({"date": date, "amount": amount, "category": row.get("category", "").strip()})
    return expenses

def aggregate_monthly(expenses: list[dict]) -> dict:
    monthly = defaultdict(float)
    for exp in expenses:
        key = exp["date"].strftime("%Y-%m")
        monthly[key] += exp["amount"]
    # Sort by month
    return dict(sorted(monthly.items()))

def top_categories(expenses: list[dict], n: int = 5) -> list[tuple[str, float]]:
    cat_totals = Counter()
    for exp in expenses:
        cat = exp["category"] or "Uncategorized"
        cat_totals[cat] += exp["amount"]
    return cat_totals.most_common(n)

def ascii_bar_chart(values: dict, max_width: int, currency: str) -> str:
    if not values:
        return "(no data)"
    max_val = max(values.values())
    scale = max_width / max_val if max_val else 0
    lines = []
    for month, amount in values.items():
        bar_len = int(amount * scale)
        bar = "█" * bar_len
        lines.append(f"{month}: {bar} {currency}{amount:,.2f}")
    return "\n".join(lines)

def main() -> None:
    args = parse_args()
    expenses = read_expenses(args.file, args.date_format)
    if not expenses:
        sys.exit("No expense records found.")

    monthly = aggregate_monthly(expenses)
    top_cats = top_categories(expenses)

    print("\n=== Monthly Expense Summary ===")
    for month, total in monthly.items():
        print(f"{month}: {args.currency}{total:,.2f}")

    print("\n=== Top Categories ===")
    for cat, total in top_cats:
        print(f"{cat}: {args.currency}{total:,.2f}")

    print("\n=== Expense Trend (ASCII Chart) ===")
    print(ascii_bar_chart(monthly, args.width, args.currency))

if __name__ == "__main__":
    main()
