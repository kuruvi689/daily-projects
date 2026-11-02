# Expense Forecast CLI

A lightweight, CPU‑only Python CLI that turns a simple CSV of personal or business expenses into actionable insights:

- **Monthly aggregation** by category
- **Anomaly detection** (spikes > × threshold of the category median)
- **Next‑month cash‑flow forecast** using a rolling average of the same calendar month
- **One‑click JSON export** suitable for feeding into dashboards, SaaS billing, or automated alerts

## Why this is SaaS‑ready
- **Micro‑service friendly** – expose the CLI via a tiny FastAPI wrapper or run as a scheduled job on Railway/Vercel.
- **Modular core** – `load_expenses`, `aggregate_monthly`, `forecast_next_month`, and `detect_anomalies` are pure functions that can be imported into larger systems (e.g., a finance dashboard or a budgeting SaaS).
- **Zero external dependencies** – only the Python standard library, keeping hosting costs low.
- **CPU‑only Windows support** – works on any Windows laptop (i5, no GPU required).

## Installation
```bash
pip install -r requirements.txt   # currently empty – stdlib only
```

## Usage
```bash
python main.py expenses.csv --output summary.json --threshold 2.5
```
- `expenses.csv` must contain `date,amount,category,description` columns (date in `YYYY-MM-DD`).
- `--threshold` controls how aggressive anomaly detection is (default 2.0).

The command creates `summary.json`:
```json
{
  "monthly_totals": {
    "2024-01": {"food": 320.5, "transport": 120.0},
    "...": {}
  },
  "next_month_forecast": {"year": 2024, "month": 11, "forecast": 845.3},
  "anomalies": [
    {"date": "2024-01-15", "category": "travel", "amount": 780.0, "description": "flight"}
  ]
}
```

## Extending the tool
- Plug into a **FastAPI** endpoint to turn the CLI into an HTTP micro‑service.
- Replace the simple average forecast with a time‑series model (still CPU‑friendly) for higher‑tier plans.
- Add authentication and multi‑tenant storage to monetize as a $5‑20/month SaaS.

## Tags
#AIMastery #Strategy #Finance
