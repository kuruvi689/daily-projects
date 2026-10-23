import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Simple scoring heuristics for unsecured business loan leads
#  - Revenue > 5L => +2 points
#  - Existing credit score >= 650 => +2 points
#  - Requested amount <= 10% of annual revenue => +1 point
#  - Business age >= 2 years => +1 point
#  - No prior loan defaults => +2 points
#  Total max points = 8. Higher score = higher priority.

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score Suryoday loan leads and output ranked CSV"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to input CSV containing lead data",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Path to write ranked output CSV",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Only output top N leads (default: all)",
    )
    return parser.parse_args()

def read_leads(csv_path: Path) -> List[Dict[str, Any]]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = [row for row in reader]
    return leads

def safe_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_int(value: str) -> int:
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def score_lead(lead: Dict[str, Any]) -> int:
    score = 0
    revenue = safe_float(lead.get("annual_revenue_lakh", 0))
    credit_score = safe_int(lead.get("credit_score", 0))
    requested = safe_float(lead.get("requested_amount_lakh", 0))
    business_age = safe_int(lead.get("business_age_years", 0))
    prior_default = lead.get("prior_default", "no").strip().lower()

    if revenue > 5:
        score += 2
    if credit_score >= 650:
        score += 2
    if revenue > 0 and requested <= 0.1 * revenue:
        score += 1
    if business_age >= 2:
        score += 1
    if prior_default == "no":
        score += 2
    return score

def enrich_and_rank(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for lead in leads:
        lead["score"] = score_lead(lead)
    ranked = sorted(leads, key=lambda x: x["score"], reverse=True)
    return ranked

def write_output(leads: List[Dict[str, Any]], out_path: Path, top: int | None):
    fieldnames = list(leads[0].keys()) if leads else []
    if top is not None:
        leads = leads[:top]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

def main() -> None:
    args = parse_args()
    if not args.input.is_file():
        sys.exit(f"Input file not found: {args.input}")
    leads = read_leads(args.input)
    if not leads:
        sys.exit("No leads found in input CSV.")
    ranked = enrich_and_rank(leads)
    write_output(ranked, args.output, args.top)
    print(f"Scored {len(ranked)} leads. Output written to {args.output}")

if __name__ == "__main__":
    main()
