# Loan Lead Optimizer Lite 🚀

A tiny Python CLI that **ranks small‑business loan leads** for Suryoday Bank (or any fintech) and exports the best candidates as JSON/CSV.

## 🎯 Aim
- **Financial Independence** – turn raw lead lists into high‑conversion pipelines.
- **Micro‑SaaS ready** – price at $5‑20 / month per user (API‑less, CSV‑based).
- **Modular** – core scoring logic lives in `score_lead` & `rank_leads` and can be imported by larger n8n or FastAPI services.

## ✨ Features
- Simple CSV input (no DB required).
- Heuristic scoring using credit score, loan amount, and recency of contact.
- Configurable top‑N output.
- Export to JSON **or** CSV for downstream automation (n8n, Zapier, etc.).
- Pure‑Python, standard‑library only – runs on a Windows CPU box.

## 🛠️ Stack
- Python 3.9+
- Standard library (`argparse`, `csv`, `json`, `datetime`)

## 🚀 Quick Start
```bash
# Clone & install (no extra packages)
git clone https://github.com/yourname/loan-lead-optimizer-lite.git
cd loan-lead-optimizer-lite
python -m venv .venv && .venv\Scripts\activate
python main.py leads.csv --top 15 --json ranked.json --csv ranked.csv
```

## 📂 Input format (leads.csv)
| name | contact | amount | purpose | credit_score | last_contact |
|------|---------|--------|---------|--------------|--------------|
| John Doe | 9876543210 | 250000 | Expansion | 720 | 2024-09-15 |

*All columns are optional except `name` and `amount`; missing values are safely handled.*

## 📤 Output
- **Console** – ranked list with scores.
- **JSON/CSV** – ready for import into n8n, Google Sheets, or your own SaaS backend.

## 🧩 Extending
Import the scoring functions:
```python
from main import score_lead, rank_leads
```
Wrap them in a FastAPI endpoint or an n8n function node to build a full‑stack lead‑gen service.

## 💰 SaaS Model
- **Tier 1** – $5/mo: 5,000 leads/month, CSV only.
- **Tier 2** – $12/mo: 20,000 leads, JSON + CSV, email alerts.
- **Tier 3** – $20/mo: Unlimited, custom scoring weights, priority support.

## 🏷️ Tags
#AIMastery #Strategy #Finance

## License
MIT – free for personal and commercial use.
