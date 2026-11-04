# loan‑lead‑qualifier

*A lightweight CLI to score and filter SMB loan leads for Suryoday Bank*  

## 🎯 Aim
Help a small‑finance team turn a raw CSV of loan enquiries into a short, high‑quality list ready for outreach. The tool applies deterministic business rules, produces a transparent **qualification_score**, and can be offered as a $5‑20 /month SaaS micro‑service (API wrapper or hosted CLI).

## 🚀 Features
- **Zero‑dependency** – pure Python standard library, runs on any Windows CPU box.
- Configurable **score threshold** (default 0.6).
- Simple, explainable heuristics: revenue, years in business, credit score, request size, industry risk.
- Outputs a new CSV with an added `qualification_score` column.
- Designed as a **module** – `score_lead` can be imported by larger pipelines (n8n, Railway, etc.).

## 🛠️ Installation
```bash
pip install loan-lead-qualifier   # if published to PyPI
# or, for a local dev copy
git clone https://github.com/yourname/loan-lead-qualifier.git
cd loan-lead-qualifier
python -m pip install -r requirements.txt   # empty for stdlib only
```

## 📋 Usage
```bash
python main.py leads_raw.csv -o qualified.csv -t 0.65
```
- `leads_raw.csv` – input with columns: `annual_revenue, years_in_business, credit_score, requested_amount, industry` (case‑insensitive).
- `-o` – destination file (defaults to `qualified_leads.csv`).
- `-t` – minimum score to keep a lead.

The CLI prints a summary and writes the filtered CSV.

## 📦 SaaS‑ready wrapper (concept)
Expose the `score_lead` function via a tiny FastAPI endpoint (or Railway function). Charge per month for a limited number of API calls (e.g., 5 k leads).

## 🏷️ Tags
#AIMastery #Strategy #Finance

## 📄 License
MIT – free for commercial use.
