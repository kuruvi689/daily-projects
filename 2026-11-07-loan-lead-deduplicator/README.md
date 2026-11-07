# loan-lead-deduplicator

A tiny, **CPU‑only** Python CLI that cleans up raw loan‑lead CSVs for Suryoday Small Finance Bank. It removes duplicate entries based on email or phone, merges source information, and outputs ready‑to‑import CSV plus an audit JSON.

---

## 🎯 Aim
- **Financial Independence** – turn lead‑gen noise into higher conversion rates.
- **#AIMastery #Strategy #Finance**
- Build a micro‑service that can be packaged as a SaaS offering ($5‑20 / month) for any SMB doing loan or credit lead generation.

---

## Features
- **Zero‑dependency** – pure standard‑library implementation.
- Detects duplicates via **email (case‑insensitive)** or **phone** (normalizes to last 10 digits).
- Merges `source` fields so you never lose channel attribution.
- Generates:
  - `unique_leads.csv` – clean file ready for import.
  - `duplicates.json` – full audit for compliance.
- Simple CLI with optional JSON dump to stdout.

---

## Installation
```bash
# Clone the repo (or copy main.py) and run directly – no packages required.
python -m venv .venv && .venv\\Scripts\\activate  # Windows
python main.py --help
```

---

## Usage
```bash
python main.py raw_leads.csv --out cleaned_output
```
- `raw_leads.csv` must contain headers: **name,email,phone,source**.
- Output directory will be created if missing.
- Add `--json` to also print a detailed duplicate list.

---

## SaaS‑Ready Blueprint
1. **Wrap** this script in a FastAPI endpoint that accepts file uploads.
2. **Persist** results to cloud storage (e.g., Railway + S3).  
3. **Bill** per month via Stripe/Razorpay – $5‑20 based on processed rows.
4. **Scale** horizontally – the core logic lives in `deduplicate()` and can be reused in larger pipelines (n8n, Airflow, etc.).

---

## Development
- Run tests locally by creating a small CSV and executing the CLI.
- Extend by adding fuzzy email matching or external validation APIs if needed.

---

## License
MIT – free for personal and commercial use.
