import argparse
import json
import sys
from datetime import datetime, date
from typing import List, Tuple

def parse_date(date_str: str) -> date:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")

def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month + (1 if end.day >= start.day else 0)

def load_history(path: str) -> List[Tuple[date, float]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [(datetime.strptime(item["date"], "%Y-%m-%d").date(), float(item["balance"])) for item in data]
    except Exception as e:
        sys.stderr.write(f"Error loading history: {e}\n")
        return []

def average_monthly_savings(history: List[Tuple[date, float]]) -> float:
    if len(history) < 2:
        return 0.0
    # sort by date
    history.sort(key=lambda x: x[0])
    total_months = months_between(history[0][0], history[-1][0])
    if total_months == 0:
        return 0.0
    total_saved = history[-1][1] - history[0][1]
    return total_saved / total_months

def projection(current_balance: float, monthly_income: float, monthly_expense: float, target_amount: float, target_date: date) -> Tuple[float, int, float]:
    today = date.today()
    months_left = months_between(today, target_date)
    if months_left <= 0:
        raise ValueError("Target date must be in the future.")
    net_monthly = monthly_income - monthly_expense
    required_total = target_amount - current_balance
    required_monthly = required_total / months_left
    return required_monthly, months_left, net_monthly

def suggest_adjustments(required_monthly: float, net_monthly: float) -> str:
    if required_monthly <= net_monthly:
        return "You can meet the goal with your current cash‑flow. Consider increasing savings to reach earlier or add a safety buffer."
    deficit = required_monthly - net_monthly
    # simple suggestions
    suggestions = []
    # 1. Reduce expense by 10% increments until feasible
    reduced_expense = net_monthly + deficit
    suggestions.append(f"Reduce monthly expenses by approximately ${deficit:,.2f} (e.g., cut discretionary spend).")
    # 2. Increase income
    suggestions.append(f"Increase monthly income by ${deficit:,.2f} (e.g., side‑gig, freelance).")
    return " | ".join(suggestions)

def main() -> None:
    parser = argparse.ArgumentParser(description="Financial Goal Projection CLI – estimate required savings to hit a target.")
    parser.add_argument("--balance", type=float, required=True, help="Current account balance.")
    parser.add_argument("--income", type=float, required=True, help="Expected monthly income.")
    parser.add_argument("--expense", type=float, required=True, help="Expected monthly expense.")
    parser.add_argument("--target", type=float, required=True, help="Desired amount at target date.")
    parser.add_argument("--date", type=parse_date, required=True, help="Target date (YYYY-MM-DD).")
    parser.add_argument("--history", type=str, default=None, help="Path to JSON file with past balances for trend analysis. Format: [{\"date\": \"YYYY-MM-DD\", \"balance\": number}, ...]")
    args = parser.parse_args()

    try:
        required_monthly, months_left, net_monthly = projection(
            args.balance, args.income, args.expense, args.target, args.date
        )
    except ValueError as ve:
        parser.error(str(ve))
        return

    output = {
        "current_balance": args.balance,
        "target_amount": args.target,
        "target_date": args.date.isoformat(),
        "months_remaining": months_left,
        "required_monthly_savings": round(required_monthly, 2),
        "net_monthly_cashflow": round(net_monthly, 2),
        "feasibility": required_monthly <= net_monthly,
    }

    # optional trend analysis
    if args.history:
        history = load_history(args.history)
        avg_save = average_monthly_savings(history)
        output["average_monthly_savings_past"] = round(avg_save, 2)
        output["trend_gap"] = round(required_monthly - avg_save, 2)

    output["suggestion"] = suggest_adjustments(required_monthly, net_monthly)

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
