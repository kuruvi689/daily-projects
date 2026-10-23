# Suryoday Loan Lead Scoring CLI

A tiny, SaaS‑ready Python CLI that scores and ranks unsecured business loan leads for **Suryoday Small Finance Bank**.

## 🎯 Aim
- **Financial Independence**: Turn lead‑gen into a revenue stream by offering a micro‑service ($5‑20/mo) that instantly prioritises high‑quality prospects.
- **Strategy**: Simple heuristic scoring that any founder can plug into larger n8n or Railway workflows.
- **Automation**: Run nightly on a cheap Windows VM, output a ranked CSV ready for sales outreach.

## ✨ Features
- Reads a CSV of raw leads (any column names, see *sample*).
- Applies a transparent 0‑8 point scoring model based on revenue, credit score, request size, business age, and default history.
- Outputs a ranked CSV with an added `score` column.
- Optional `--top N` to return only the best leads.
- Zero‑cost: pure standard‑library, works on CPU‑only Windows.

## 📦 Installation
```bash
pip install -r requirements.txt   # empty for stdlib only
```

## 🚀 Usage
```bash
python main.py leads_raw.csv ranked_leads.csv --top 50
```
- `leads_raw.csv` – your raw lead export.
- `ranked_leads.csv` – scored, descending order.
- `--top` – limit output to the top N leads (optional).

## 🗂 Input CSV format (minimum columns)
| Column | Description |
|--------|-------------|
| `annual_revenue_lakh` | Annual revenue in lakhs (numeric) |
| `credit_score` | Credit bureau score |
| `requested_amount_lakh` | Loan amount requested |
| `business_age_years` | Age of the business |
| `prior_default` | `yes` or `no` – any prior loan defaults |

Additional columns are preserved untouched.

## 🛠 Extensibility
- **Modular scoring**: `score_lead` is a pure function – import it into n8n, FastAPI, or a larger SaaS backend.
- **Custom heuristics**: Fork and tweak the point system without touching the CLI plumbing.
- **Integration**: Pipe output to email automation, CRM import, or a Slack notification bot.

## 📈 Business Model
Offer this as a hosted service:
- **Tier 1** – 5 $/month for up to 1 000 leads per month.
- **Tier 2** – 15 $/month for up to 10 000 leads, with API access.
- **Tier 3** – 20 $/month for unlimited leads + webhook callbacks.

## 🏷 Tags
#AIMastery #Strategy #Finance

## License
MIT – free for commercial use.
