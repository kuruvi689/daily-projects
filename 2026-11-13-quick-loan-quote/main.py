# main.py
"""quick-loan-quote: A lightweight CLI to generate instant loan eligibility quotes
for Suryoday Small Finance Bank's unsecured business loans.

Features:
- Accepts key business metrics via command line arguments or interactive prompts.
- Applies a rule‑based scoring model (revenue, tenure, credit‑score proxy, existing debt).
- Calculates a maximum loan amount and suggested interest rate.
- Outputs a concise markdown report that can be emailed or posted to a web hook.
- All logic is pure Python stdlib – suitable for CPU‑only Windows machines.

Usage examples:
  python main.py --revenue 1200000 --tenure 3 --credit 720 --debt 200000
  python main.py            # will prompt for inputs interactively
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a quick loan quote.")
    parser.add_argument("--revenue", type=float, help="Annual revenue (INR)")
    parser.add_argument("--tenure", type=float, help="Business age in years")
    parser.add_argument("--credit", type=int, help="Credit score (300‑900)")
    parser.add_argument("--debt", type=float, help="Existing total debt (INR)")
    parser.add_argument("--output", type=Path, default=Path("quote.md"), help="File to write markdown report")
    return parser.parse_args()

def prompt_missing(args: argparse.Namespace) -> None:
    def ask(prompt: str, cast):
        while True:
            try:
                return cast(input(prompt))
            except Exception:
                print("Invalid value, try again.")
    if args.revenue is None:
        args.revenue = ask("Annual revenue (INR): ", float)
    if args.tenure is None:
        args.tenure = ask("Business age (years): ", float)
    if args.credit is None:
        args.credit = ask("Credit score (300‑900): ", int)
    if args.debt is None:
        args.debt = ask("Existing debt (INR): ", float)

def eligibility_score(revenue: float, tenure: float, credit: int, debt: float) -> float:
    """Simple weighted scoring (0‑100). Higher is better.
    - Revenue weight: 0.4 (scaled log10)
    - Tenure weight: 0.2 (0‑5 years = 0‑20 points, >5 = 20)
    - Credit weight: 0.3 (linear)
    - Debt weight: 0.1 (lower debt improves score)
    """
    import math
    rev_score = min(40, 40 * (math.log10(max(revenue, 1)) / 6))  # assume 1‑1,000,0000 log10≈6
    tenure_score = 20 if tenure >= 5 else (tenure / 5) * 20
    credit_score = (credit - 300) / 600 * 30  # 300‑900 maps to 0‑30
    debt_score = max(0, 10 - (debt / revenue) * 10)  # if debt = 0 →10, debt = revenue →0
    total = rev_score + tenure_score + credit_score + debt_score
    return round(total, 2)

def compute_quote(score: float) -> dict:
    """Derive loan amount and interest rate from score.
    - Max loan = 20% of annual revenue * (score/100)
    - Interest rate = base 12% - (score‑50)*0.05% (capped 8‑15%)
    """
    # placeholder revenue for calculation; will be filled by caller
    return {
        "max_loan": None,
        "interest_rate": None,
        "score": score,
    }

def generate_report(data: dict, revenue: float) -> str:
    max_loan = round(revenue * 0.20 * (data["score"] / 100), 2)
    ir = 12 - max(0, (data["score"] - 50) * 0.05)
    ir = round(min(max(ir, 8), 15), 2)
    data["max_loan"] = max_loan
    data["interest_rate"] = ir
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"""# Quick Loan Quote
*Generated: {now}*

**Eligibility Score:** {data['score']}/100

- **Maximum Loan Amount:** ₹{max_loan:,.2f}
- **Suggested Interest Rate:** {ir}% per annum

*This is a provisional estimate. Final terms are subject to bank underwriting.*
"""
    return md

def main() -> None:
    args = parse_args()
    prompt_missing(args)
    score = eligibility_score(args.revenue, args.tenure, args.credit, args.debt)
    quote_data = {"score": score}
    report = generate_report(quote_data, args.revenue)
    # Write markdown
    args.output.write_text(report, encoding="utf-8")
    print(f"Quote written to {args.output}")
    # Also emit JSON for API consumption
    json_path = args.output.with_suffix('.json')
    json_path.write_text(json.dumps({
        "score": score,
        "max_loan": quote_data["max_loan"],
        "interest_rate": quote_data["interest_rate"],
        "generated_at": datetime.now().isoformat()
    }, indent=2), encoding="utf-8")
    print(f"Machine‑readable JSON saved to {json_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nOperation cancelled by user.")
