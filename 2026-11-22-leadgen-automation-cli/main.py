import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Constants
DATA_DIR = Path.cwd() / "data"
LEADS_FILE = DATA_DIR / "leads.csv"
OUTPUT_DIR = Path.cwd() / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not LEADS_FILE.exists():
        with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "name", "mobile", "email", "source", "status"])

def load_leads() -> List[Dict[str, str]]:
    leads = []
    with open(LEADS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads

def save_lead(lead: Dict[str, str]):
    with open(LEADS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            lead["timestamp"],
            lead["name"],
            lead["mobile"],
            lead["email"],
            lead["source"],
            lead["status"],
        ])

def add_lead(args: argparse.Namespace):
    lead = {
        "timestamp": datetime.utcnow().isoformat(),
        "name": args.name,
        "mobile": args.mobile,
        "email": args.email,
        "source": args.source or "unknown",
        "status": "new",
    }
    save_lead(lead)
    print(f"✅ Lead added for {lead['name']}")

def list_leads(args: argparse.Namespace):
    leads = load_leads()
    if args.status:
        leads = [l for l in leads if l["status"] == args.status]
    if not leads:
        print("No leads found.")
        return
    for i, lead in enumerate(leads, 1):
        print(f"{i}. {lead['name']} | {lead['mobile']} | {lead['email']} | {lead['source']} | {lead['status']} | {lead['timestamp']}")

def update_status(args: argparse.Namespace):
    leads = load_leads()
    idx = args.index - 1
    if idx < 0 or idx >= len(leads):
        print("❌ Invalid lead index")
        return
    leads[idx]["status"] = args.status
    # rewrite file
    with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "name", "mobile", "email", "source", "status"])
        writer.writeheader()
        writer.writerows(leads)
    print(f"✅ Lead #{args.index} status updated to {args.status}")

def export_json(args: argparse.Namespace):
    leads = load_leads()
    out_path = OUTPUT_DIR / (args.filename or "leads.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)
    print(f"✅ Exported {len(leads)} leads to {out_path}")

def stats(args: argparse.Namespace):
    leads = load_leads()
    total = len(leads)
    statuses = {}
    for l in leads:
        statuses[l["status"]] = statuses.get(l["status"], 0) + 1
    print(f"Total leads: {total}")
    for status, count in statuses.items():
        print(f"  {status}: {count}")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="leadgen-automation-cli",
        description="Lightweight lead management for Suryoday Bank loan outreach",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add a new lead")
    add.add_argument("--name", required=True, help="Lead full name")
    add.add_argument("--mobile", required=True, help="Mobile number")
    add.add_argument("--email", required=True, help="Email address")
    add.add_argument("--source", help="Lead source (e.g., fb_ads, referral)")
    add.set_defaults(func=add_lead)

    lst = sub.add_parser("list", help="List stored leads")
    lst.add_argument("--status", help="Filter by status")
    lst.set_defaults(func=list_leads)

    upd = sub.add_parser("update", help="Update lead status")
    upd.add_argument("index", type=int, help="Lead number from list command")
    upd.add_argument("--status", required=True, choices=["new", "contacted", "qualified", "lost"], help="New status")
    upd.set_defaults(func=update_status)

    exp = sub.add_parser("export", help="Export leads to JSON")
    exp.add_argument("--filename", help="Output filename (default leads.json)")
    exp.set_defaults(func=export_json)

    st = sub.add_parser("stats", help="Show simple statistics")
    st.set_defaults(func=stats)

    return parser

def main():
    ensure_data_dir()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
