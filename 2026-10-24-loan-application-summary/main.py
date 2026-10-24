import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# -------------------------- Helper Functions --------------------------

def load_csv(path: Path):
    """Load CSV and return list of dict rows."""
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def sanitize_email(email: str) -> str:
    """Very light email validation / normalization.
    Returns empty string if email looks invalid.
    """
    email = email.strip().lower()
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return email
    return ""

def parse_amount(value: str) -> float:
    """Parse monetary strings like "$1,200.50" or "1200" into float."""
    value = value.replace("$", "").replace(",", "").strip()
    try:
        return float(value)
    except ValueError:
        return 0.0

def month_key(date_str: str) -> str:
    """Return YYYY-MM from various date formats."""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            continue
    return "unknown"

# -------------------------- Core Logic --------------------------

def summarize_applications(rows):
    """Create a summary dict from raw application rows.
    Expected columns (case‑insensitive):
        applicant_name, email, phone, loan_amount, application_date, status
    """
    summary = {
        "total_applications": 0,
        "total_approved": 0,
        "total_rejected": 0,
        "total_pending": 0,
        "total_amount_requested": 0.0,
        "total_amount_approved": 0.0,
        "monthly_breakdown": defaultdict(lambda: {"applications": 0, "approved": 0, "rejected": 0, "pending": 0}),
        "cleaned_records": [],
    }

    for row in rows:
        summary["total_applications"] += 1
        amount = parse_amount(row.get("loan_amount", "0"))
        summary["total_amount_requested"] += amount
        status = row.get("status", "pending").strip().lower()
        month = month_key(row.get("application_date", ""))
        mb = summary["monthly_breakdown"][month]
        mb["applications"] += 1
        if status == "approved":
            summary["total_approved"] += 1
            summary["total_amount_approved"] += amount
            mb["approved"] += 1
        elif status == "rejected":
            summary["total_rejected"] += 1
            mb["rejected"] += 1
        else:
            summary["total_pending"] += 1
            mb["pending"] += 1

        # Clean email & drop rows with no usable contact info
        email = sanitize_email(row.get("email", ""))
        phone = re.sub(r"[^0-9+]", "", row.get("phone", "")).strip()
        if not email and not phone:
            continue
        cleaned = {
            "name": row.get("applicant_name", "").strip(),
            "email": email,
            "phone": phone,
            "loan_amount": amount,
            "application_date": row.get("application_date", "").strip(),
            "status": status,
        }
        summary["cleaned_records"].append(cleaned)

    # Convert defaultdict to plain dict for JSON serialisation
    summary["monthly_breakdown"] = dict(summary["monthly_breakdown"])
    return summary

def export_json(summary: dict, out_path: Path):
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

def export_csv_cleaned(records: list, out_path: Path):
    if not records:
        return
    fieldnames = ["name", "email", "phone", "loan_amount", "application_date", "status"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

# -------------------------- CLI Interface --------------------------

def build_parser():
    p = argparse.ArgumentParser(
        description="Summarise loan applications and produce clean, SaaS‑ready output."
    )
    p.add_argument("input", type=Path, help="Path to input CSV file containing raw applications.")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path.cwd() / "loan_summary",
        help="Directory where JSON and cleaned CSV will be written.",
    )
    p.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip exporting the cleaned CSV (useful if only summary is needed).",
    )
    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input.is_file():
        sys.exit(f"❌ Input file not found: {args.input}")

    rows = load_csv(args.input)
    if not rows:
        sys.exit("❌ CSV appears empty or malformed.")

    summary = summarize_applications(rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "summary.json"
    export_json(summary, json_path)
    print(f"✅ Summary written to {json_path}")

    if not args.no_clean:
        csv_path = args.out_dir / "cleaned_applications.csv"
        export_csv_cleaned(summary["cleaned_records"], csv_path)
        print(f"✅ Cleaned records written to {csv_path}")

    # Small on‑screen report for quick insight
    print("\n--- Quick Stats ---")
    print(f"Total applications : {summary['total_applications']}")
    print(f"Approved           : {summary['total_approved']} (${summary['total_amount_approved']:.2f})")
    print(f"Rejected           : {summary['total_rejected']}")
    print(f"Pending            : {summary['total_pending']}")
    print(f"Requested amount   : ${summary['total_amount_requested']:.2f}")

if __name__ == "__main__":
    main()
