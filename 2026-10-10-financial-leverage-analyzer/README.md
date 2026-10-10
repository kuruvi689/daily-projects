# financial-leverage-analyzer

A tiny, CPU‑only Python CLI that turns a plain CSV of expenses into a **leverage‑focused** markdown report.

## 🎯 Aim
- Identify which categories consume the bulk of your cash (high‑leverage spend).
- Spot outlier transactions that may indicate fraud, waste, or missed optimisation.
- Produce a ready‑to‑share markdown summary – perfect for newsletters, dashboards, or SaaS‑style email reports.

## 📦 Features
- **Zero‑dependency** (standard library only) – runs on any Windows machine.
- Modular core (`load_expenses`, `categorize`, `detect_outliers`, `markdown_*`) that can be imported into larger services.
- Configurable keyword‑to‑category mapping via a simple `category_map.json`.
- Two sub‑commands:
  - `summary` – overall spend, leverage score, top categories.
  - `outliers` – transactions deviating > σ from their category mean.
- Output to **stdout** or a file (`-o` flag).

## 🚀 Quick Start
```bash
# Install (no external packages required)
git clone https://github.com/yourname/financial-leverage-analyzer
cd financial-leverage-analyzer
python -m venv .venv && .venv\Scripts\activate
# Prepare a CSV (date,amount,description,category?)
# Example row: 2024-09-01,125.50,"Starbucks coffee", 
python main.py expenses.csv summary -o report.md
python main.py expenses.csv outliers -s 2.5 > outliers.md
```

## 📂 Expected CSV format
| Column      | Description                                    |
|------------|------------------------------------------------|
| `date`     | ISO date (`YYYY-MM-DD`) or `DD/MM/YYYY`        |
| `amount`   | Numeric (positive = spend, negative = refund) |
| `description` | Free‑text description of the transaction      |
| `category` *(optional)* | Manual category; if blank the tool auto‑categorises |

## 🛠️ Custom Category Mapping
Create `category_map.json` in the project root, e.g.:
```json
{
  "uber": "transport",
  "lyft": "transport",
  "starbucks": "food",
  "rent": "housing"
}
```
The mapper is case‑insensitive and matches keywords anywhere in the description.

## 💡 SaaS‑ready
- **Pricing model**: $5–$20 / month per user for hosted markdown generation via a tiny Flask wrapper.
- **Scalability**: Core logic is pure functions – drop‑in to any backend (FastAPI, Azure Functions, etc.).
- **Security**: No external calls, all data stays on‑premise.

## 🏷️ Tags
#AIMastery #Strategy #Finance

## License
MIT – free for personal and commercial use.
