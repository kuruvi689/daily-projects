# Lead Email Generator

**Category:** #Finance #AIMastery #Strategy

A tiny Python CLI that turns a CSV of leads into ready‑to‑send, personalized email drafts.

## Why this matters
- **Revenue tool** – automate the first outreach step for Suryoday loan leads or Teddy3 wholesale contacts.
- **Micro‑SaaS ready** – charge $5‑20 / month for a hosted version that pulls leads from Google Sheets and emails the drafts.
- **Modular** – core `generate_emails` can be imported into larger n8n or Railway workflows.

## Features
- Reads any CSV with a header row (e.g., `name,email,company,loan_amount`).
- Uses a plain‑text template with `$placeholder` syntax that maps to CSV columns.
- Outputs each email separated by `---` for easy copy‑paste or further processing.
- Zero‑dependency (standard library only).

## Installation
```bash
pip install lead-email-generator   # if published on PyPI
# or use the source directly
python -m venv .venv && .venv\\Scripts\\activate
pip install -r requirements.txt  # empty for stdlib
```

## Usage
```bash
python main.py leads.csv email_template.txt -o drafts.txt
```
- `leads.csv` – your lead list.
- `email_template.txt` – e.g.:
```
Hi $name,
\nI noticed $company is looking for financing up to $loan_amount. Our partnership with Suryoday Bank can get you a quick, unsecured business loan.
\nBest,\nSivanesh
```
- `drafts.txt` will contain one email per lead, separated by `---`.

## Running as a SaaS (quick sketch)
1. Deploy the CLI on Railway or Vercel as a lightweight HTTP endpoint.
2. Accept a multipart request with CSV and template files.
3. Return the generated drafts as plain text or JSON.
4. Add Stripe/ Razorpay for subscription billing ($5‑20 / month).

## Development
```bash
python -m unittest discover tests   # add your own tests
```

## License
MIT – free for commercial use.
