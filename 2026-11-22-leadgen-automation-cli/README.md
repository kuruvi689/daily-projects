# leadgen-automation-cli

A tiny, self‑hosted Python CLI to capture, manage and export loan‑lead data for **Suryoday Small Finance Bank** outreach campaigns.

## 🎯 Aim
- Replace manual Google Sheet entry with a reproducible, version‑controlled workflow.
- Provide a SaaS‑ready backend that can be wrapped in a tiny Flask/FastAPI service for a $5‑20 /month subscription.
- Keep the core logic (CSV handling, status updates, stats) completely framework‑agnostic so it can be reused in larger automation pipelines (n8n, Railway, etc.).

## ✨ Features
- **add** – store a new lead (name, mobile, email, source).
- **list** – view all leads, optionally filtered by status.
- **update** – change a lead’s status (`new`, `contacted`, `qualified`, `lost`).
- **export** – dump the CSV to a JSON file ready for downstream APIs.
- **stats** – quick counts per status.

## 🛠️ Tech Stack
- **Python 3.10+** (standard library only).
- CSV for persistent storage (lightweight, no DB required).
- Optional JSON export for integration with other services.

## 📦 Installation
```bash
# Clone the repo
git clone https://github.com/yourname/leadgen-automation-cli.git
cd leadgen-automation-cli

# (Optional) create a virtual env
python -m venv .venv && .\.venv\Scripts\activate

# Install requirements (none for stdlib only)
pip install -r requirements.txt
```

## 🚀 Usage
```bash
# Add a lead
python main.py add --name "Ravi Kumar" --mobile 9876543210 \
    --email ravi@example.com --source fb_ads

# List all leads
python main.py list

# Update status of lead #2 to qualified
python main.py update 2 --status qualified

# Export to JSON
python main.py export --filename todays_leads.json

# Show stats
python main.py stats
```

## 📈 SaaS‑Ready Path
1. Wrap `main.py` functions in a tiny FastAPI app.
2. Deploy on Railway or Vercel (serverless) – the CSV file lives on a mounted volume or switched to SQLite for persistence.
3. Add API key auth and a simple billing layer (Stripe) to charge $5‑20 per month per user.
4. Offer a web UI that calls the same endpoints – the CLI remains the developer‑friendly interface.

## 🏷️ Tags
#AIMastery #Strategy #Finance

---
*Built for Sivanesh, Teddy3 & the Suryoday loan team – a lean tool that turns lead capture into a repeatable micro‑service.*
