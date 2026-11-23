# Expense Pattern Detector

A lightweight Python CLI that ingests a simple CSV of personal or business expenses, groups them by month, highlights out‑of‑pattern spend, and emits a clean JSON summary ready for dashboards or SaaS‑style reporting.

## Features
- **Monthly aggregation** – total spend and per‑category breakdown.
- **Anomaly detection** – flags any transaction > *N*× the median of its category (default = 2×).
- **Zero‑dependency** – pure standard‑library implementation; runs on any CPU‑only Windows box.
- **SaaS‑ready output** – one JSON file per month, ideal for feeding a micro‑service, webhook, or static site.

## Installation
```bash
pip install expense-pattern-detector  # if packaged, otherwise just copy main.py
```

## Usage
```bash
python main.py expenses.csv [--out-dir reports] [--threshold 2.5]
```
- `expenses.csv` must contain `date,amount,category,description` columns (date in `YYYY-MM-DD`).
- `--out-dir` sets where JSON reports are written (default `expense_reports`).
- `--threshold` adjusts the anomaly multiplier.

## Example CSV
```csv
date,amount,category,description
2026-10-01,45.20,food,lunch
2026-10-03,1200,travel,flight to Bangalore
2026-10-15,23.99,entertainment,streaming
```

## Output (sample `2026-10_summary.json`)
```json
{
  "month": "2026-10",
  "total_spent": 1269.19,
  "by_category": {
    "food": 45.2,
    "travel": 1200.0,
    "entertainment": 23.99
  },
  "anomalies": [
    {
      "date": "2026-10-03",
      "amount": 1200.0,
      "category": "travel",
      "description": "flight to Bangalore"
    }
  ]
}
```

## Why it matters
- **#AIMastery** – leverages simple statistical heuristics for automated spend monitoring.
- **#Strategy** – equips freelancers and small‑biz owners with data‑driven expense insights without costly BI tools.
- **#Finance** – helps users spot waste early, supporting better cash‑flow and budgeting decisions.

## Extensibility
- Import `load_expenses`, `summarize_month`, `detect_anomalies` in larger Python services.
- Swap the CSV loader for a database query or an API pull.
- Replace the median‑based rule with ML models (e.g., isolation forest) when you upgrade hardware.

## License
MIT – free for commercial and personal use.
