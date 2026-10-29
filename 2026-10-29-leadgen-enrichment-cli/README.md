# LeadGen Enrichment CLI

A tiny, SaaS‑ready Python command‑line tool that **adds value to loan‑lead lists** for Suryoday Bank or any micro‑finance operation.

## 🎯 Aim
- Generate a *pseudo credit score* (300‑850) from an email hash and reported revenue – no external credit‑bureau integration required.
- Enrich each record with **latitude / longitude** using the free OpenStreetMap Nominatim API.
- Output a ready‑to‑import CSV that can be fed into downstream scoring pipelines or CRM systems.

## 📦 Features (modular core)
1. **Deterministic scoring** – repeatable across runs, useful for A/B testing.
2. **Geo‑lookup** – optional, works on any address string.
3. **Dry‑run mode** – see added columns without hitting the API (great for CI).
4. **Zero‑GPU, CPU‑only** – pure Python, works on a Windows i5.
5. **SaaS‑ready** – wrap the CLI in a tiny Flask/FastAPI wrapper and charge $5‑20/mo per 5k enriched rows.

## 🛠️ Installation
```bash
pip install -r requirements.txt   # only 'requests' is required, but stdlib works as‑is
```
If you keep the default (empty) requirements, the script runs with the standard library only.

## 🚀 Usage
```bash
python main.py leads_raw.csv leads_enriched.csv
# optional dry‑run
python main.py leads_raw.csv leads_enriched.csv --dry-run
```
- **Input CSV** must contain at least `email`, `address`, and `annual_revenue` columns.
- **Output CSV** retains original columns plus:
  - `pseudo_credit_score`
  - `lat`, `lon`
  - `enriched_at`

## 📈 SaaS Business Model
- **Tier 1** – up to 5 000 rows / month → $5 / mo.
- **Tier 2** – 5 001‑20 000 rows → $12 / mo.
- **Tier 3** – 20 001+ rows → $20 / mo.
Pricing can be enforced by a lightweight Flask wrapper that checks a per‑user quota.

## 🧩 Extensibility
The core `enrich_lead` function is pure Python and can be imported into larger pipelines (e.g., n8n nodes, Railway workers, or Vercel serverless functions).

## 🏷️ Tags
#AIMastery #Strategy #Finance
