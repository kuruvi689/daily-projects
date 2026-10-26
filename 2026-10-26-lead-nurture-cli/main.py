import argparse
import csv
import json
import os
import sys
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path

CONFIG_PATH = Path.home() / ".lead_nurture_config.json"

DEFAULT_CONFIG = {
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "smtp_user": "user@example.com",
    "smtp_password": "password",
    "from_email": "nurture@example.com",
    "template": "Hi {name},\n\nWe noticed you showed interest in a {product} loan on {date}. Let us know if you have any questions or would like to proceed.\n\nBest,\nYour Team",
    "follow_up_days": [3, 7, 14]
}

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # write default config for first‑time users
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"Created default config at {CONFIG_PATH}. Please edit it before running again.")
        sys.exit(1)

def parse_leads(csv_path: str):
    leads = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Expected columns: name,email,product,lead_date (YYYY-MM-DD)
            try:
                lead_date = datetime.strptime(row["lead_date"], "%Y-%m-%d").date()
            except Exception:
                print(f"Skipping row with invalid date: {row}")
                continue
            leads.append({
                "name": row.get("name", "").strip(),
                "email": row.get("email", "").strip(),
                "product": row.get("product", "").strip(),
                "lead_date": lead_date,
            })
    return leads

def due_for_followup(lead, today, follow_days):
    days_since = (today - lead["lead_date"]).days
    return days_since in follow_days

def send_email(cfg, to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["from_email"]
    msg["To"] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
            server.starttls()
            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.send_message(msg)
        print(f"Sent to {to_email}")
    except Exception as e:
        print(f"Failed to send to {to_email}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Lead Nurture CLI – auto‑email follow‑ups for loan leads")
    parser.add_argument("csv", help="Path to leads CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Print emails without sending")
    args = parser.parse_args()

    cfg = load_config()
    leads = parse_leads(args.csv)
    today = datetime.utcnow().date()
    follow_days = cfg.get("follow_up_days", [3, 7, 14])

    for lead in leads:
        if not lead["email"]:
            continue
        if due_for_followup(lead, today, follow_days):
            subject = f"Your {lead['product']} loan inquiry – next steps"
            body = cfg["template"].format(
                name=lead["name"] or "Friend",
                product=lead["product"],
                date=lead["lead_date"].isoformat(),
            )
            if args.dry_run:
                print("---\nTo:", lead["email"], "\nSubject:", subject, "\nBody:\n", body, "\n---")
            else:
                send_email(cfg, lead["email"], subject, body)

if __name__ == "__main__":
    main()
