import csv
import sys
import argparse
from pathlib import Path
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(
        description="Score and filter SMB loan leads for Suryoday Bank"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to CSV file containing raw leads",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("qualified_leads.csv"),
        help="Where to write qualified leads (default: qualified_leads.csv)",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.6,
        help="Minimum score (0‑1) a lead must reach to be kept",
    )
    return parser.parse_args()

def load_leads(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        sys.exit("❌ No data found in input file")
    return rows, reader.fieldnames

def score_lead(lead: dict) -> float:
    """Return a 0‑1 score based on simple business‑logic rules.

    Expected columns (case‑insensitive):
    - annual_revenue (numeric, USD)
    - years_in_business (numeric)
    - credit_score (0‑900)
    - requested_amount (numeric, USD)
    - industry (string)
    """
    # Normalise keys to lower case for resilience
    l = {k.lower(): v for k, v in lead.items()}
    try:
        rev = float(l.get("annual_revenue", 0))
        years = float(l.get("years_in_business", 0))
        credit = float(l.get("credit_score", 0))
        amount = float(l.get("requested_amount", 0))
    except ValueError:
        return 0.0

    # Simple heuristics – each component contributes equally
    rev_score = min(rev / 500_000, 1)          # >=500k gets full points
    years_score = min(years / 5, 1)           # >=5 years gets full points
    credit_score = min(credit / 750, 1)       # >=750 gets full points
    amount_score = 1 - min(amount / 1_000_000, 1)  # smaller requests are better

    # Industry weighting – favour low‑risk sectors
    low_risk = {"retail", "services", "manufacturing"}
    industry = l.get("industry", "").strip().lower()
    industry_score = 1.0 if industry in low_risk else 0.7

    overall = (rev_score + years_score + credit_score + amount_score + industry_score) / 5
    return round(overall, 3)

def annotate_and_filter(rows, threshold):
    qualified = []
    for row in rows:
        score = score_lead(row)
        row["qualification_score"] = f"{score:.3f}"
        if score >= threshold:
            qualified.append(row)
    return qualified

def write_csv(rows, fieldnames, path: Path):
    # Ensure the new column is present
    if "qualification_score" not in fieldnames:
        fieldnames.append("qualification_score")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    args = parse_args()
    rows, fieldnames = load_leads(args.input)
    qualified = annotate_and_filter(rows, args.threshold)
    write_csv(qualified, fieldnames, args.output)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"✅ {len(qualified)} leads written to {args.output} (run @ {now})")

if __name__ == "__main__":
    main()
