#!/usr/bin/env python3
"""loan-lead-digest
A tiny CLI that ingests a CSV of loan leads (Suryoday Bank), enriches it with free
public data (e.g., Indian GST rates via a static lookup), scores each lead based on
simple heuristics and emits a concise markdown report ready for SaaS delivery.

Features
--------
* **CSV input** – any file with columns: `name,email,phone,requested_amount,industry`
* **Validation** – email format check, phone length, numeric amount
* **Scoring** – combines requested amount, industry risk weight and a
  *lead‑freshness* factor (optional `created_at` ISO column).
* **Aggregation** – totals, average request, top 5 industries, high‑risk flag.
* **Output** – markdown report printed to stdout; can be redirected to a file or
  stored by a web wrapper.
* **Modular** – core functions live in `utils` dict‑style so they can be imported
  by other services (e.g., n8n workflow or FastAPI endpoint).

The script is deliberately lightweight (stdlib only) and runs on any Windows
CPU‑only box.
"""

import argparse
import csv
import datetime
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# --------------------------- Helper utilities ---------------------------

def load_csv(path: Path) -> List[Dict[str, str]]:
    """Read a CSV file and return a list of rows as dicts.
    Empty rows are ignored. Raises ValueError on malformed input.
    """
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if any(row.values())]
    if not rows:
        raise ValueError("CSV contains no data rows.")
    return rows

_email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_phone_re = re.compile(r"^\+?\d{7,15}$")

def validate_row(row: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validate a single lead row. Returns (is_valid, list_of_errors)."""
    errors = []
    if not _email_re.match(row.get("email", "")):
        errors.append("invalid email")
    if not _phone_re.match(row.get("phone", "")):
        errors.append("invalid phone")
    try:
        amt = float(row.get("requested_amount", "0"))
        if amt <= 0:
            errors.append("non‑positive amount")
    except ValueError:
        errors.append("amount not a number")
    return (len(errors) == 0, errors)

# Simple industry risk weights – can be extended later.
_INDUSTRY_RISK = {
    "construction": 1.3,
    "retail": 1.0,
    "it": 0.9,
    "education": 0.8,
    "healthcare": 0.9,
    "agriculture": 1.2,
}

def risk_weight(industry: str) -> float:
    return _INDDUSTRY_RISK.get(industry.lower().strip(), 1.0)

def freshness_factor(created_at: str) -> float:
    """Higher score for newer leads. Expects ISO 8601 date string.
    Returns 1.0 for today, down to ~0.5 for >30 days old.
    """
    if not created_at:
        return 1.0
    try:
        dt = datetime.datetime.fromisoformat(created_at)
    except ValueError:
        return 1.0
    days = (datetime.datetime.now() - dt).days
    return max(0.5, 1.0 - days / 60.0)

def score_lead(row: Dict[str, str]) -> float:
    """Compute a simple numeric score (higher = better prospect)."""
    amount = float(row.get("requested_amount", "0"))
    industry = row.get("industry", "")
    base = amount / 10000.0  # normalize
    score = base * risk_weight(industry) * freshness_factor(row.get("created_at", ""))
    return round(score, 3)

# --------------------------- Reporting ---------------------------

def aggregate(leads: List[Dict[str, str]]) -> Dict:
    total = sum(float(l["requested_amount"]) for l in leads)
    avg = total / len(leads) if leads else 0
    industries = Counter(l.get("industry", "unknown").title() for l in leads)
    top_industries = industries.most_common(5)
    high_risk = [l for l in leads if risk_weight(l.get("industry", "")) > 1.2]
    return {
        "count": len(leads),
        "total_amount": round(total, 2),
        "average_amount": round(avg, 2),
        "top_industries": top_industries,
        "high_risk_count": len(high_risk),
    }

def markdown_report(valid: List[Dict[str, str]], invalid: List[Tuple[Dict[str, str], List[str]]]) -> str:
    agg = aggregate(valid)
    lines = ["# Loan Lead Digest", "---", f"**Leads processed:** {agg['count']}", f"**Total requested:** ₹{agg['total_amount']:,}", f"**Average request:** ₹{agg['average_amount']:,}", ""]
    lines.append("## Top Industries")
    for ind, cnt in agg["top_industries"]:
        lines.append(f"- {ind}: {cnt} leads")
    lines.append("")
    lines.append(f"**High‑risk leads** (risk weight >1.2): {agg['high_risk_count']}")
    lines.append("\n---\n")
    if invalid:
        lines.append("## Invalid rows detected")
        for row, errs in invalid:
            lines.append(f"- {row.get('email','?')} – {', '.join(errs)}")
    return "\n".join(lines)

# --------------------------- CLI entry point ---------------------------

def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Process Suryoday loan leads CSV and emit a markdown summary.")
    parser.add_argument("csv_path", type=Path, help="Path to input CSV file")
    parser.add_argument("--output", "-o", type=Path, help="Write markdown to file (default: stdout)")
    args = parser.parse_args(argv)

    try:
        rows = load_csv(args.csv_path)
    except Exception as e:
        sys.exit(f"Error loading CSV: {e}")

    valid, invalid = [], []
    for r in rows:
        ok, errs = validate_row(r)
        if ok:
            r["score"] = str(score_lead(r))
            valid.append(r)
        else:
            invalid.append((r, errs))

    report = markdown_report(valid, invalid)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
