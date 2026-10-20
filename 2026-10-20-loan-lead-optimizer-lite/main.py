import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime


def load_leads(file_path):
    """Load leads from a CSV file. Expected columns: name, contact, amount, purpose, credit_score, last_contact (YYYY-MM-DD)"""
    leads = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize fields
            row['amount'] = float(row.get('amount', 0) or 0)
            row['credit_score'] = int(row.get('credit_score', 0) or 0)
            try:
                row['last_contact'] = datetime.strptime(row.get('last_contact', ''), "%Y-%m-%d").date()
            except Exception:
                row['last_contact'] = None
            leads.append(row)
    return leads


def score_lead(lead, today=None):
    """Simple heuristic score (0‑100) for loan lead quality.
    Higher credit score, larger amount, recent contact = higher score.
    """
    if today is None:
        today = datetime.today().date()
    # Base from credit score (0‑850) scaled to 0‑50
    credit_part = min(max(lead['credit_score'], 0), 850) / 850 * 50
    # Amount part: log scaling, max 30 points
    amount = lead['amount']
    amount_part = 0
    if amount > 0:
        import math
        amount_part = min(math.log1p(amount) / math.log1p(500000) * 30, 30)  # assume 500k max
    # Recency part: last contact within 30 days gives up to 20 points
    recency_part = 0
    if lead['last_contact']:
        days = (today - lead['last_contact']).days
        if days < 0:
            days = 0
        recency_part = max(0, 20 - (days / 30) * 20)
    # Purpose sanity check – if purpose missing, penalize 5 points
    purpose_penalty = 0 if lead.get('purpose') else -5
    total = credit_part + amount_part + recency_part + purpose_penalty
    return round(max(0, min(total, 100)), 2)


def rank_leads(leads, top_n=10):
    scored = []
    for lead in leads:
        lead_score = score_lead(lead)
        lead_copy = lead.copy()
        lead_copy['score'] = lead_score
        scored.append(lead_copy)
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_n]


def export_json(leads, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(leads, f, default=str, indent=2)
    print(f"✅ Exported {len(leads)} leads to {out_path}")


def export_csv(leads, out_path):
    if not leads:
        print("⚠️ No leads to export")
        return
    fieldnames = list(leads[0].keys())
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead)
    print(f"✅ Exported {len(leads)} leads to {out_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Loan Lead Optimizer – rank and export small‑business loan leads for Suryoday Bank"
    )
    parser.add_argument('input', help='Path to input CSV file containing raw leads')
    parser.add_argument('--top', type=int, default=10, help='Number of top leads to output')
    parser.add_argument('--json', help='Path to write ranked leads as JSON')
    parser.add_argument('--csv', help='Path to write ranked leads as CSV')
    return parser.parse_args()


def main():
    args = parse_args()
    if not os.path.isfile(args.input):
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)
    leads = load_leads(args.input)
    if not leads:
        print("⚠️ No leads loaded from input")
        sys.exit(0)
    top_leads = rank_leads(leads, top_n=args.top)
    print("--- Top Leads ---")
    for i, lead in enumerate(top_leads, 1):
        print(f"{i}. {lead['name']} – Score: {lead['score']} – Amount: {lead['amount']:,} – Credit: {lead['credit_score']}")
    if args.json:
        export_json(top_leads, args.json)
    if args.csv:
        export_csv(top_leads, args.csv)

if __name__ == "__main__":
    main()
