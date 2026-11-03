# Financial Goal Projection CLI

A lightweight, CPU‑only Python tool that helps individuals **project** the monthly savings needed to hit a financial target. Perfect for personal finance SaaS, micro‑consulting, or embedding into larger budgeting platforms.

## Features
- **Goal calculator** – input current balance, income, expense, target amount & date.
- **Feasibility check** – tells you if your cash‑flow can meet the goal.
- **Adjustment suggestions** – simple actions (reduce expense / increase income) when the goal is out of reach.
- **Trend analysis (optional)** – import a JSON history of past balances to compare against actual savings.
- No external dependencies – works with the Python standard library only.

## Installation
```bash
pip install financial-goal-projection-cli
```
*(If you publish to PyPI; otherwise clone the repo and run `python -m pip install .`)*

## Usage
```bash
python main.py \
  --balance 12000 \
  --income 5000 \
  --expense 3500 \
  --target 30000 \
  --date 2027-12-31 \
  --history past_balances.json
```
The command prints a JSON summary:
```json
{
  "current_balance": 12000,
  "target_amount": 30000,
  "target_date": "2027-12-31",
  "months_remaining": 13,
  "required_monthly_savings": 1384.62,
  "net_monthly_cashflow": 1500,
  "feasibility": true,
  "suggestion": "You can meet the goal with your current cash‑flow..."
}
```

## JSON History Format (optional)
```json
[
  {"date": "2024-01-01", "balance": 10000},
  {"date": "2024-02-01", "balance": 10800},
  ...
]
```
The CLI will compute the average past monthly savings and show the gap to the required rate.

## SaaS‑Ready
- **Pricing**: $5‑$20/month per user for API access or hosted CLI.
- **Modular**: Core functions (`projection`, `suggest_adjustments`, `average_monthly_savings`) can be imported as a library.
- **Deployable** on Railway, Railway‑Lite, or any Windows/Linux container.

## Tags
#AIMastery #Strategy #Finance

## License
MIT – free for commercial and personal use.
