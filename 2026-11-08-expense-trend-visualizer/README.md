# Expense Trend Visualizer

**Category:** #AIMastery #Finance #Strategy

A lightweight, CPU‑only Python CLI that turns a simple CSV of your daily expenses into a clear monthly summary and an ASCII bar‑chart trend. Perfect as a micro‑SaaS ($5‑20 / month) for personal finance dashboards, fintech onboarding tools, or as a reusable component in larger budgeting platforms.

---

## Features
- **Zero‑dependency** – works with the Python standard library only.
- Parses any CSV with `date` and `amount` columns (optional `category`).
- Monthly totals, top‑5 spending categories, and a printable ASCII bar chart.
- Fully configurable date format, currency symbol, and chart width.
- Small footprint: < 250 lines, runs on any Windows machine without a GPU.

---

## Installation
```bash
pip install expense-trend-visualizer  # if packaged, otherwise clone repo
```

## Usage
```bash
python main.py expenses.csv               # default YYYY‑MM‑DD dates
python main.py expenses.csv -d "%d/%m/%Y" -c "₹" -w 60
```
**CSV format example**
```csv
date,amount,category
2024-01-05,45.20,Food
2024-01-12,120.00,Transport
2024-02-01,250.00,Rent
```

The tool prints:
- Monthly totals
- Top 5 categories
- An ASCII bar chart visualising the trend over time.

---

## API (Modular Core)
The core functions (`read_expenses`, `aggregate_monthly`, `top_categories`, `ascii_bar_chart`) are import‑able, enabling integration into SaaS back‑ends, Flask APIs, or n8n automations.

---

## Extending
- Swap `ascii_bar_chart` for a Matplotlib plot (add `matplotlib` to `requirements`).
- Persist monthly aggregates to a DB for multi‑user SaaS.
- Add anomaly detection on month‑over‑month spikes.

---

## License
MIT – free for commercial and personal use.
