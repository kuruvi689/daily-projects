# Budget Forecast CLI

**Tag:** #AIMastery #Strategy #Finance

## Overview
`budget-forecast-cli` is a lightweight Python command‑line tool that turns a CSV of historic expenses into a simple 3‑month (configurable) budget forecast. It aggregates spending by category, computes recent averages, and projects those averages forward. The output is a clean JSON file that can be consumed by SaaS dashboards, chat‑bots, or any downstream service.

## Why It Matters
- **Micro‑service ready:** Small, stateless, and can be wrapped in a Docker container or hosted on Railway/Vercel as a $5‑20/month API.
- **Modular core:** Functions (`load_expenses`, `aggregate_monthly`, `average_monthly_spend`, `forecast`) are pure and reusable in larger finance platforms.
- **Zero‑cost:** Relies only on the Python standard library – perfect for CPU‑only Windows machines.
- **Actionable output:** JSON forecast can be fed directly into budgeting apps, email reports, or Slack bots.

## Installation
```bash
pip install -r requirements.txt   # requirements.txt is empty (standard library only)
```

## Usage
```bash
python main.py --input expenses.csv [--output forecast.json] [--period 3]
```
- **expenses.csv** – must contain `date` (YYYY‑MM‑DD), `amount` (numeric), and `category` columns.
- **--period** – number of future months to forecast (default 3).
- **--output** – destination JSON file (default `forecast.json`).

### Example CSV
```csv
date,amount,category
2024-07-01,120.50,groceries
2024-07-03,45.00,transport
2024-07-15,200.00,entertainment
```

### Sample Output
```json
{
  "forecast": [
    {
      "month": "2024-08",
      "forecast": {
        "groceries": 115.33,
        "transport": 40.00,
        "entertainment": 180.20
      }
    },
    {
      "month": "2024-09",
      "forecast": { ... }
    }
  ]
}
```

## Extending the Tool
- **API wrapper:** Expose `forecast` via FastAPI for SaaS consumption.
- **Visualization:** Add a Matplotlib/Plotly chart generator (optional dependency).
- **Custom weighting:** Pass a `--weight` argument to give more importance to recent months.

## License
MIT – free for commercial and personal use.
