# loan-lead-digest

**Category**: #Finance #AIMastery #Strategy

## AIM
Provide Suryoday Small Finance Bank (or any loan‑originator) a lightweight, automated way to turn raw lead CSV dumps into a clean, actionable markdown summary that can be emailed to sales, displayed in a dashboard, or fed into a SaaS subscription.

## Why it matters
* **Revenue tool** – Turn a repetitive manual spreadsheet job into a sell‑able micro‑service ($5‑20 /mo per user).
* **Founder‑friendly** – Runs on a plain Windows laptop, no GPU, no external services.
* **Modular** – Core functions (`load_csv`, `validate_row`, `score_lead`, `aggregate`) are importable for n8n, FastAPI, or Railway back‑ends.

## Features
- Validate emails, phone numbers and request amounts.
- Score each lead using amount, industry risk, and freshness.
- Summarise total/average request, top industries, high‑risk count.
- Output a ready‑to‑publish markdown report.
- Zero‑dependency (standard library only).

## Installation
```bash
# Clone the repo (or copy the single file)
git clone https://github.com/yourname/loan-lead-digest.git
cd loan-lead-digest
# No extra packages required
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

## Usage
```bash
python main.py leads.csv           # prints markdown to console
python main.py leads.csv -o report.md   # writes to file
```
`leads.csv` must contain at least:
```
name,email,phone,requested_amount,industry,created_at
John Doe,john@example.com,+919876543210,250000,Construction,2024-10-01T12:00:00
```
`created_at` is optional; if omitted the lead is treated as fresh.

## Extending / SaaS integration
- **API wrapper** – import `loan_lead_digest.utils` (the functions in this file) and expose via FastAPI.
- **Scheduler** – run nightly with Windows Task Scheduler or Railway cron.
- **Pricing** – charge per processed lead or per generated report.

## License
MIT – free for personal and commercial use.
