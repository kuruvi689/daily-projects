# Leverage Matrix Analyzer

A lightweight Python CLI that turns raw pricing data into **strategic leverage insights** for B2B SaaS, e‑commerce, or finance teams.

## 🎯 Aim
- Identify products where you can **raise price** or **improve margin** without losing competitiveness.
- Produce a concise markdown report and a machine‑readable JSON payload ready for integration into dashboards or billing engines.

## ✨ Features
- Pure‑Python, **CPU‑only**, works on Windows.
- Accepts two CSV files (your catalog & competitor pricing).
- Calculates price gap, margin gap, and a composite **Leverage Score**.
- Generates a one‑page markdown report (top 5 opportunities) and a full JSON summary.
- Fully modular – core logic (`compute_metrics`) can be imported by other services.

## 🚀 SaaS‑Ready
Package the CLI as a tiny micro‑service (e.g., Railway, Vercel Serverless) and charge $5‑20 /mo per analysis run.

## 📦 Installation
```bash
pip install -r requirements.txt   # empty – stdlib only
```

## 🛠️ Usage
```bash
python main.py your_products.csv competitor_prices.csv \
    --output my_report.md --json my_summary.json
```
- `your_products.csv` columns: `product_id,price,cost,category`
- `competitor_prices.csv` columns: `product_id,competitor_price,competitor_name`

## 📂 Output
- **Markdown report** – human‑readable executive summary.
- **JSON file** – array of objects with full metrics for downstream automation.

## 🧩 Extensibility
Import `compute_metrics` in other Python projects to embed leverage calculations into larger decision‑engine pipelines.

## 🏷️ Tags
#AIMastery #Strategy #Finance
