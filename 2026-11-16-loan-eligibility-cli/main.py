#!/usr/bin/env python3
"""loan-eligibility-cli
A tiny command‑line tool to evaluate small‑business loan eligibility for
Suryoday Bank lead data.

Features
--------
* Reads a CSV of leads (exported from any CRM).
* Applies configurable eligibility rules (turnover, credit‑score, tenure).
* Outputs a JSON list with a confidence score and recommended action.
* Designed to be packaged as a SaaS micro‑service ($5‑20/mo).

Usage
-----
    python main.py --input leads.csv \
        --output results.json \
        --min-turnover 500000 \
        --min-credit 650 \
        --min-tenure 12

All arguments are optional; defaults are suitable for a typical
micro‑loan product.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Core eligibility logic – reusable in larger systems
# ---------------------------------------------------------------------------

def evaluate_lead(lead: Dict[str, str], *, min_turnover: float, min_credit: int, min_tenure: int) -> Dict[str, Any]:
    """Return a dict with a score and suggested action for a single lead.

    Parameters
    ----------
    lead: mapping with keys `turnover`, `credit_score`, `business_tenure_months`
    min_turnover: minimum annual turnover required
    min_credit: minimum credit‑score required
    min_tenure: minimum months the business has been operating
    """
    try:
        turnover = float(lead.get("turnover", 0))
        credit = int(lead.get("credit_score", 0))
        tenure = int(lead.get("business_tenure_months", 0))
    except ValueError:
        # malformed numeric field – treat as ineligible
        return {"lead_id": lead.get("lead_id"), "eligible": False, "score": 0, "reason": "invalid data"}

    # Simple weighted scoring (each criterion 0‑1)
    turnover_score = min(turnover / min_turnover, 1.0)
    credit_score = min(credit / min_credit, 1.0)
    tenure_score = min(tenure / min_tenure, 1.0)

    # Overall confidence is the geometric mean – penalises a single weak factor
    overall = (turnover_score * credit_score * tenure_score) ** (1/3)
    eligible = overall >= 0.6  # threshold for recommendation
    action = "fast‑track" if overall >= 0.85 else "standard review" if eligible else "reject"

    return {
        "lead_id": lead.get("lead_id"),
        "eligible": eligible,
        "score": round(overall, 3),
        "action": action,
    }

# ---------------------------------------------------------------------------
# CLI handling
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate loan eligibility for Suryoday leads")
    parser.add_argument("--input", type=Path, required=True, help="Path to input CSV file")
    parser.add_argument("--output", type=Path, default=Path("eligibility.json"), help="Path for JSON results")
    parser.add_argument("--min-turnover", type=float, default=500000, help="Minimum annual turnover required")
    parser.add_argument("--min-credit", type=int, default=650, help="Minimum credit score required")
    parser.add_argument("--min-tenure", type=int, default=12, help="Minimum business tenure (months) required")
    return parser.parse_args()


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        sys.exit(f"Error: input file '{path}' not found")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_json(data: List[Dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    args = parse_args()
    leads = read_csv(args.input)
    results = [
        evaluate_lead(
            lead,
            min_turnover=args.min_turnover,
            min_credit=args.min_credit,
            min_tenure=args.min_tenure,
        )
        for lead in leads
    ]
    write_json(results, args.output)
    print(f"Processed {len(leads)} leads → {args.output}")


if __name__ == "__main__":
    main()
