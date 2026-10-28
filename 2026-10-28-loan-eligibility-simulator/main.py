#!/usr/bin/env python3
"""loan-eligibility-simulator
A tiny CLI that evaluates personal/business loan eligibility based on user‑provided financial metrics.
It is designed as a reusable library (core functions) and a thin command‑line interface.

Usage:
  python -m loan_eligibility_simulator [options]

Options:
  -h, --help          Show this help message.
  -i, --input FILE    JSON file with applicant data (default: stdin).
  -o, --output FILE   Write result JSON to FILE (default: stdout).

The JSON input schema:
{
  "monthly_income": number,
  "existing_debt": number,
  "credit_score": int (300‑850),
  "business_years": int,
  "requested_amount": number,
  "requested_term_months": int
}

The output contains a decision, an approved amount (may be lower than requested),
and a short rationale.
"""
import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import Dict, Any

# --------------------------- Core Logic ---------------------------

@dataclass
class Applicant:
    monthly_income: float
    existing_debt: float
    credit_score: int
    business_years: int
    requested_amount: float
    requested_term_months: int

@dataclass
class Decision:
    approved: bool
    approved_amount: float
    max_term_months: int
    rationale: str

def debt_to_income_ratio(app: Applicant) -> float:
    """Calculate DTI = (existing debt + projected loan payment) / income.
    The projected payment is a simple 10% of requested amount per month.
    """
    projected_payment = app.requested_amount * 0.10
    return (app.existing_debt + projected_payment) / app.monthly_income

def credit_score_factor(score: int) -> float:
    """Map credit score (300‑850) to a multiplier between 0.5 and 1.2.
    Higher score => higher multiplier.
    """
    if score < 300:
        score = 300
    if score > 850:
        score = 850
    # Linear interpolation
    return 0.5 + (score - 300) * (0.7 / 550)

def business_stability_factor(years: int) -> float:
    """Reward longer‑running businesses.
    0‑1 yr → 0.6, 2‑3 yr → 0.8, 4+ yr → 1.0
    """
    if years >= 4:
        return 1.0
    if years >= 2:
        return 0.8
    return 0.6

def evaluate(app: Applicant) -> Decision:
    # Basic eligibility checks
    if app.monthly_income <= 0:
        return Decision(False, 0, 0, "Income must be positive.")
    if app.requested_amount <= 0:
        return Decision(False, 0, 0, "Requested amount must be positive.")
    if app.credit_score < 300 or app.credit_score > 850:
        return Decision(False, 0, 0, "Credit score out of range (300‑850).")

    dti = debt_to_income_ratio(app)
    if dti > 0.45:
        return Decision(False, 0, 0, f"High debt‑to‑income ratio ({dti:.2%}).")

    # Compute a base approval amount using income and multipliers
    base_amount = app.monthly_income * 12 * credit_score_factor(app.credit_score) * business_stability_factor(app.business_years)
    # Cap at 3× annual income
    max_amount = min(base_amount, app.monthly_income * 12 * 3)
    approved_amount = min(app.requested_amount, max_amount)

    # Determine feasible term – longer terms increase risk, so cap at 60 months
    max_term = min(app.requested_term_months, 60)
    # If approved amount is far below request, suggest shorter term
    if approved_amount < app.requested_amount * 0.7:
        max_term = min(max_term, 36)

    rationale = (
        f"DTI={dti:.2%}, credit_factor={credit_score_factor(app.credit_score):.2f}, "
        f"business_factor={business_stability_factor(app.business_years):.2f}. "
        f"Approved {approved_amount:.0f} for up to {max_term} months."
    )
    return Decision(True, approved_amount, max_term, rationale)

# --------------------------- CLI Wrapper ---------------------------

def parse_args(argv: Any = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loan Eligibility Simulator")
    parser.add_argument("-i", "--input", type=argparse.FileType('r'), default=sys.stdin,
                        help="JSON input file (default: stdin)")
    parser.add_argument("-o", "--output", type=argparse.FileType('w'), default=sys.stdout,
                        help="Write result JSON (default: stdout)")
    return parser.parse_args(argv)

def main(argv: Any = None) -> None:
    args = parse_args(argv)
    try:
        data = json.load(args.input)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Invalid JSON input: {e}\n")
        sys.exit(1)
    try:
        applicant = Applicant(
            monthly_income=float(data["monthly_income"]),
            existing_debt=float(data["existing_debt"]),
            credit_score=int(data["credit_score"]),
            business_years=int(data["business_years"]),
            requested_amount=float(data["requested_amount"]),
            requested_term_months=int(data["requested_term_months"]),
        )
    except (KeyError, ValueError) as e:
        sys.stderr.write(f"Missing or malformed field: {e}\n")
        sys.exit(1)

    decision = evaluate(applicant)
    result = asdict(decision)
    json.dump(result, args.output, indent=2)
    args.output.write("\n")

if __name__ == "__main__":
    main()
