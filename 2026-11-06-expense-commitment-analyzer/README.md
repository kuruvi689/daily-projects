# Expense Commitment Analyzer

A lightweight, CPU‑only Python CLI that turns a simple CSV of your daily expenses into a **monthly financial health report** and **flags unusual spending**.

## 🎯 Goal & Value Proposition
- **Real problem** – Many freelancers and small‑business owners track expenses in spreadsheets but lack insight into *what’s changing* month‑to‑month.
- **SaaS‑ready** – Offer the CLI as a hosted micro‑service (upload CSV, get JSON/HTML report) for $5‑20 / month.
- **Modular core** – The categorisation, aggregation and anomaly logic are pure functions that can be imported into larger dashboards, bots, or finance platforms.
- **Zero‑cost stack** – Only Python standard library; no GPU, no external paid APIs.

## 📦 Installation
```bash
pip install expense-commitment-analyzer   # package name (if published)
# or install locally
git clone https://github.com/yourname/expense-commitment-analyzer
cd expense-commitment-analyzer
pip install -r requirements.txt   # empty – stdlib only
```

## 🚀 Quick Start
```bash
# Prepare a CSV (date,description,amount,currency(optional))
# Example row: 2024-03-15,Uber ride,12.50,USD
python main.py expenses.csv --out report.json
```
The tool writes `report.json` containing:
- Monthly totals
- Category breakdowns
- Any *anomalous* months where a category’s spend exceeds its historic average by > 2 σ.

## 🛠️ How It Works
1. **Load CSV** – Parses dates, amounts, optional currency (kept as‑is).
2. **Category inference** – Simple keyword matching (food, transport, entertainment, …). Extendable via a config file.
3. **Monthly aggregation** – Sums amounts per month and per category.
4. **Statistical flagging** – Computes mean & standard deviation across months; flags outliers.
5. **Export** – JSON report ready for UI rendering or further automation.

## 🔧 Extending the Core
```python
from main import simple_category, aggregate_by_month, flag_anomalies
# reuse in a Flask endpoint, a FastAPI service, or a n8n workflow
```
- Swap the keyword map for a ML‑based classifier.
- Add currency conversion via a free API (e.g., https://exchangerate.host).
- Persist data in SQLite or Google Sheets for multi‑user SaaS.

## 📈 Business Model Ideas
- **Self‑serve tier** – Upload CSV via a tiny web UI, get a downloadable report.
- **Enterprise tier** – API key, webhook callbacks, custom category vocabularies.
- **Add‑ons** – Budget recommendations, forecast next month’s spend, integration with accounting tools.

## 🏷️ Tags
#AIMastery #Strategy #Finance

---
*Built for Sivanesh’s Teddy3 brand ecosystem – lightweight, Windows‑compatible, and ready to ship as a micro‑service.*
