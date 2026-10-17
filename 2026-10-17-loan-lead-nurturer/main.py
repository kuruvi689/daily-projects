import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Score and schedule follow‑ups for Suryoday Bank loan leads"
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to CSV file containing raw leads",
    )
    parser.add_argument(
        "--output",
        required=False,
        type=Path,
        default=Path("lead_report.json"),
        help="Path to write the JSON report",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Minimum score to flag a lead as high priority (0‑1)",
    )
    parser.add_argument(
        "--followup-days",
        type=int,
        default=3,
        help="Days after which to schedule a follow‑up for low‑score leads",
    )
    return parser.parse_args()

def load_leads(csv_path: Path):
    leads = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads

def score_lead(lead: dict) -> float:
    """Very simple heuristic scoring.
    - business_type: manufacturing gets +0.2
    - requested_amount > 500000 gets +0.2
    - credit_score (0‑1000) normalized adds up to 0.4
    Returns a value between 0 and 1.
    """
    score = 0.0
    # business type weighting
    btype = lead.get("business_type", "").strip().lower()
    if btype in {"manufacturing", "retail", "services"}:
        score += 0.2
    # amount weighting
    try:
        amount = float(lead.get("requested_amount", 0))
        if amount > 500_000:
            score += 0.2
    except ValueError:
        pass
    # credit score weighting (expected 300‑900 range)
    try:
        credit = float(lead.get("credit_score", 0))
        credit_norm = max(0, min(credit, 1000)) / 1000
        score += 0.4 * credit_norm
    except ValueError:
        pass
    return min(score, 1.0)

def schedule_followup(lead: dict, days: int) -> str:
    """Return ISO‑8601 date string for a follow‑up.
    If the lead already has a "last_contact" date, add *days* to it;
    otherwise use today.
    """
    today = datetime.utcnow().date()
    last_contact_str = lead.get("last_contact", "")
    try:
        last_contact = datetime.strptime(last_contact_str, "%Y-%m-%d").date()
    except Exception:
        last_contact = today
    followup_date = last_contact + timedelta(days=days)
    return followup_date.isoformat()

def process_leads(leads, threshold, followup_days):
    processed = []
    for lead in leads:
        score = score_lead(lead)
        lead_out = {
            "lead_id": lead.get("lead_id"),
            "score": round(score, 3),
            "priority": "high" if score >= threshold else "low",
        }
        if score >= threshold:
            lead_out["action"] = "call_immediately"
        else:
            lead_out["action"] = "schedule_followup"
            lead_out["followup_date"] = schedule_followup(lead, followup_days)
        processed.append(lead_out)
    return processed

def main():
    args = parse_args()
    if not args.input.exists():
        sys.exit(f"❌ Input file {args.input} does not exist.")
    leads = load_leads(args.input)
    if not leads:
        sys.exit("❌ No leads found in the CSV.")
    report = process_leads(leads, args.threshold, args.followup_days)
    # write JSON report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Report written to {args.output}")
    # optional pretty table to stdout
    try:
        from tabulate import tabulate
        table = [(r["lead_id"], r["score"], r["priority"], r["action"]) for r in report]
        print(tabulate(table, headers=["ID", "Score", "Priority", "Action"]))
    except ImportError:
        pass

if __name__ == "__main__":
    main()
