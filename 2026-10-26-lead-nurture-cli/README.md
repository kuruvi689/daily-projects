# Lead Nurture CLI

A tiny Python‑only command‑line tool that turns a simple CSV of loan leads into automated, timed follow‑up emails. Perfect for **Suryoday Bank** lead‑gen pipelines or any micro‑SaaS that wants to charge $5‑20 / month for a hands‑off nurturing service.

## Features
- **Zero‑dependency** core (standard library only). Optional SMTP configuration via a JSON file.
- Reads a CSV with `name,email,product,lead_date` columns.
- Sends follow‑up emails on configurable day offsets (default 3, 7, 14 days after `lead_date`).
- Dry‑run mode to preview messages before sending.
- Modular functions (`parse_leads`, `due_for_followup`, `send_email`) that can be imported into larger Python services.

## Installation
```bash
pip install lead-nurture-cli  # (or copy the repo)
```

## Usage
1. **Create config** – the first run creates `~/.lead_nurture_config.json`. Edit the SMTP details and email template.
2. **Prepare leads CSV** – ensure columns: `name,email,product,lead_date` (ISO date).
3. **Run**:
```bash
python main.py path/to/leads.csv            # send real emails
python main.py path/to/leads.csv --dry-run  # preview only
```

## SaaS‑Ready
- Deploy on Railway or Vercel as a scheduled job (cron) that runs daily.
- Charge a subscription for the hosted service; the CLI can be packaged as a Docker container for multi‑tenant use.
- Extensible: plug in a database, add analytics, or replace SMTP with an email‑API (SendGrid, Mailgun) – the core logic stays unchanged.

## Tags
#AIMastery #Strategy #Finance

## License
MIT – free for personal and commercial use.
