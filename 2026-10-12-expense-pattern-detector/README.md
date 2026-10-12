# Expense Pattern Detector

A lightweight **Python CLI** that ingests a CSV of personal or business expenses, groups them by category, flags unusually large transactions, and generates a concise markdown summary.

## Why this matters
- **#AIMastery** – Uses statistical outlier detection (mean + 2 σ) without any external AI services.
- **#Strategy** – Turns raw spend data into actionable insights for budgeting, loan‑lead optimization, or SaaS‑style expense‑monitoring.
- **#Finance** – Helps founders like Sivanesh keep a pulse on cash‑flow, spot fraud, and present clean monthly reports to stakeholders.

## Features
- CSV input (`date,category,amount,description`).
- Category aggregation with totals, counts, and averages.
- Automatic anomaly detection per category.
- Monthly spend breakdown.
- Markdown report – ready to paste into Notion, GitHub, or email.
- Pure‑standard‑library, runs on any Windows CPU‑only machine.

## Installation
```bash
pip install expense-pattern-detector  # if packaged
# or just copy main.py to your project directory
```

## Usage
```bash
python main.py expenses.csv -o summary.md
```
- `expenses.csv` – your expense export (bank, QuickBooks, etc.).
- `-o` – optional output file; omit to print to console.

## CSV format example
```csv
date,category,amount,description
2026-09-01,Food,12.50,Lunch at cafe
2026-09-02,Transport,2.75,Metro ticket
2026-09-03,Software,49.99,Monthly SaaS subscription
```

## Extending the tool
The core functions (`load_expenses`, `group_by_category`, `detect_anomalies`, `monthly_summary`) are **modular** and can be imported into larger Python services, e.g., a Flask API for a micro‑SaaS offering.

## License
MIT – free for personal and commercial use.
