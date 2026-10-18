# Expense Anomaly Notifier

A lightweight, CPU‑only Python CLI that scans your personal or business expense CSV, flags unusually large transactions, and produces a concise monthly summary. Ideal as a micro‑SaaS offering for budgeting‑aware users.

## Features
- **Automatic grouping** by month and category.
- **Anomaly detection** using a simple multiplier over the monthly average spend (configurable).
- **JSON report** with totals, averages, category breakdowns, and flagged anomalies.
- **Human‑readable summary** printed to the console.
- No external dependencies – pure standard library, perfect for Windows machines without a GPU.

## Installation
```bash
pip install expense-anomaly-notifier  # (if packaged) or clone the repo
```

## Usage
```bash
python main.py --input expenses.csv [--output report.json] [--threshold 2.5]
```
- `expenses.csv` must contain columns: `date` (YYYY‑MM‑DD), `amount`, `category`, `description` (optional).
- `--threshold` sets how many times above the monthly average a transaction must be to be considered anomalous.

## Example CSV
```csv
date,amount,category,description
2026-09-01,45.20,food,lunch
2026-09-02,1200.00,travel,flight ticket
2026-09-15,30.00,entertainment,concert
```

## Output
- **Console**: one‑line summary per month.
- **JSON file** (`report.json` by default) containing detailed statistics and a list of anomalies.

## SaaS‑Ready
Wrap the CLI in a tiny Flask/FastAPI endpoint or a serverless function to expose a `POST /analyze` API. Charge a low monthly subscription ($5‑$20) for automated expense health checks.

## Extensibility
- Replace CSV loader with Google Sheets or Firebase integration.
- Plug in a more sophisticated ML model for anomaly detection while keeping the core logic unchanged.
- Export to PDF/HTML for client‑facing reports.

## License
MIT – free for personal and commercial use.

## Tags
#AIMastery #Strategy #Finance
