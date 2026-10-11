import csv
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Simple heuristic weights (can be tuned later)
WEIGHTS = {
    "annual_revenue": 0.4,  # higher revenue -> better score
    "credit_score": 0.4,    # higher credit score -> better score
    "existing_loans": -0.2  # more existing loans -> lower score
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score and rank loan leads for Suryoday Bank using lightweight heuristics."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to CSV file containing raw leads. Required columns: name, email, phone, annual_revenue, credit_score, existing_loans"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("scored_leads.json"),
        help="File to write scored leads (JSON)."
    )
    parser.add_argument(
        "-t",
        "--top",
        type=int,
        default=10,
        help="Number of top leads to display in console."
    )
    return parser.parse_args()

def read_csv(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        sys.exit(f"[Error] Input file not found: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"name", "email", "phone", "annual_revenue", "credit_score", "existing_loans"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"[Error] Missing required columns: {', '.join(missing)}")
        rows = []
        for row in reader:
            try:
                row["annual_revenue"] = float(row["annual_revenue"])
                row["credit_score"] = float(row["credit_score"])
                row["existing_loans"] = int(row["existing_loans"])
            except ValueError as e:
                sys.exit(f"[Error] Invalid numeric value in row {reader.line_num}: {e}")
            rows.append(row)
        return rows

def score_lead(lead: Dict[str, Any]) -> float:
    """Calculate a composite score using the WEIGHTS dictionary.
    The score is normalized to 0‑100.
    """
    # Normalisation helpers – simple min‑max based on plausible ranges
    rev_norm = min(max(lead["annual_revenue"] / 1_000_000, 0), 1)  # 0‑1M+ revenue
    credit_norm = min(max(lead["credit_score"] / 900, 0), 1)      # credit score up to 900
    loans_norm = 1 - min(max(lead["existing_loans"] / 10, 0), 1)   # 0‑10+ existing loans

    score = (
        rev_norm * WEIGHTS["annual_revenue"] +
        credit_norm * WEIGHTS["credit_score"] +
        loans_norm * abs(WEIGHTS["existing_loans"]) * (1 if WEIGHTS["existing_loans"] < 0 else -1)
    )
    return round(score * 100, 2)

def process_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for lead in leads:
        lead["score"] = score_lead(lead)
    # Sort descending by score
    return sorted(leads, key=lambda x: x["score"], reverse=True)

def write_output(leads: List[Dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)

def display_top(leads: List[Dict[str, Any]], top_n: int) -> None:
    print(f"Top {top_n} loan leads (score out of 100):")
    print("-" * 50)
    for lead in leads[:top_n]:
        print(f"{lead['name']} | Score: {lead['score']} | Revenue: {lead['annual_revenue']:.0f} | Credit: {lead['credit_score']} | Existing Loans: {lead['existing_loans']}")
    print("-" * 50)

def main() -> None:
    args = parse_args()
    raw_leads = read_csv(args.input)
    scored = process_leads(raw_leads)
    write_output(scored, args.output)
    display_top(scored, args.top)

if __name__ == "__main__":
    main()
