# LeadGen Cleaner

A tiny, Python‑only CLI that validates lead‑generation CSVs for **Suryoday Small Finance Bank** loan campaigns.

## 🎯 Aim
- **Revenue tool** – sell as a SaaS micro‑service ($5‑20 / month) to loan officers and fintech partners.
- **Modular core** – validation functions (`is_valid_email`, `is_valid_phone`, `is_valid_gstin`) are pure Python and can be imported into larger pipelines (n8n, Railway, Vercel, etc.).
- **Zero‑cost** – uses only the standard library; no GPU or heavy dependencies.

## ⚙️ Features
- Reads any CSV with configurable column names.
- Validates:
  - Email (RFC‑5322 lightweight regex)
  - Indian mobile phone numbers (handles `+91`, `0` prefixes)
  - GSTIN (15‑character format)
- Drops rows that fail any check and writes a clean CSV.
- Emits a JSON summary (total, accepted, rejected, error breakdown) – perfect for dashboards.

## 🚀 Usage
```bash
python main.py leads_raw.csv leads_clean.csv \
    --email-col Email --phone-col Mobile --gstin-col GSTIN
```
The command prints a JSON report like:
```json
{
  "total_rows": 1240,
  "accepted": 1103,
  "rejected": 137,
  "bad_email": 45,
  "bad_phone": 92,
  "bad_gstin": 0
}
```

## 📦 SaaS Packaging
1. Wrap the CLI in a Docker image (≈30 MB) – deploy on Railway or Railway‑like cheap containers.
2. Expose a tiny HTTP endpoint (`/clean`) that forwards the CSV to the CLI via a subprocess; charge per month per API key.
3. Use the JSON summary for billing (e.g., $0.01 per 100 clean rows).

## 🛠️ Development
```bash
# clone & run locally
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # empty for stdlib only
python main.py sample.csv out.csv
```

## 📚 Tags
#AIMastery #Strategy #Finance
