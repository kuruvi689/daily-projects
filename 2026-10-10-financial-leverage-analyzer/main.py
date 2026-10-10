#!/usr/bin/env python3
"""financial-leverage-analyzer

A lightweight CLI tool that reads a CSV of personal/business expenses,
identifies high‑leverage (high‑impact) spending patterns and flags outliers.
It produces a concise markdown summary that can be emailed or posted to a
dashboard. Designed to be SaaS‑ready as a micro‑service (e.g. $5‑20/month).

Features
--------
- Pure‑Python, stdlib only – runs on any Windows CPU‑only machine.
- Modular core logic (`load_expenses`, `categorize`, `detect_outliers`,
  `summarize`) can be imported by other services.
- Command‑line interface with sub‑commands `summary` and `outliers`.
- Configurable category mapping via a simple JSON file.
- Outputs markdown to stdout or a file.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Any

# ---------- Core Logic ----------

def load_expenses(csv_path: Path) -> List[Dict[str, Any]]:
    """Load expenses from a CSV file.

    Expected columns: date, amount, description, [category]
    - date: ISO format (YYYY‑MM‑DD) or any format parseable by `datetime.fromisoformat`.
    - amount: numeric (positive for spend, negative for refunds).
    - description: free text.
    - category: optional, will be auto‑categorized if missing.
    """
    expenses = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date = datetime.fromisoformat(row["date"]).date()
            except Exception:
                # fallback: try common formats
                date = datetime.strptime(row["date"], "%d/%m/%Y").date()
            amount = float(row["amount"].replace(",", ""))
            desc = row.get("description", "").strip()
            cat = row.get("category", "").strip() or None
            expenses.append({"date": date, "amount": amount, "description": desc, "category": cat})
    return expenses

def load_category_map(json_path: Path) -> Dict[str, str]:
    """Load a simple keyword → category mapping.

    Example JSON: {"uber": "transport", "starbucks": "food", "rent": "housing"}
    Matching is case‑insensitive and looks for the keyword anywhere in the description.
    """
    if not json_path.is_file():
        return {}
    with json_path.open(encoding="utf-8") as f:
        return {k.lower(): v.lower() for k, v in json.load(f).items()}

def categorize(expenses: List[Dict[str, Any]], mapping: Dict[str, str]) -> None:
    """Assign categories in‑place using the keyword map.
    Unmatched items get the category "uncategorized".
    """
    for exp in expenses:
        if exp["category"]:
            continue
        desc = exp["description"].lower()
        for kw, cat in mapping.items():
            if kw in desc:
                exp["category"] = cat
                break
        else:
            exp["category"] = "uncategorized"

def aggregate_by_category(expenses: List[Dict[str, Any]]) -> Dict[str, float]:
    totals = defaultdict(float)
    for exp in expenses:
        totals[exp["category"]] += exp["amount"]
    return dict(totals)

def detect_outliers(expenses: List[Dict[str, Any]], sigma: float = 2.0) -> List[Dict[str, Any]]:
    """Return expenses whose amount deviates more than `sigma` standard deviations
    from the mean of its category.
    """
    # Compute mean and std per category
    cat_vals: Dict[str, List[float]] = defaultdict(list)
    for exp in expenses:
        cat_vals[exp["category"]].append(exp["amount"])
    stats: Dict[str, Tuple[float, float]] = {}
    for cat, vals in cat_vals.items():
        mean = sum(vals) / len(vals)
        var = sum((x - mean) ** 2 for x in vals) / len(vals)
        std = var ** 0.5
        stats[cat] = (mean, std)
    outliers = []
    for exp in expenses:
        mean, std = stats[exp["category"]]
        if std == 0:
            continue
        if abs(exp["amount"] - mean) > sigma * std:
            outliers.append(exp)
    return outliers

def markdown_summary(expenses: List[Dict[str, Any]]) -> str:
    """Create a markdown report with totals, top categories and a simple leverage score.
    Leverage score = (total spend on top 3 categories) / (total spend) * 100.
    """
    total_spend = sum(e["amount"] for e in expenses)
    cat_totals = Counter({cat: amt for cat, amt in aggregate_by_category(expenses).items()})
    top3 = cat_totals.most_common(3)
    top_spend = sum(amt for _, amt in top3)
    leverage = (top_spend / total_spend * 100) if total_spend else 0

    lines = ["# Expense Leverage Summary", ""]
    lines.append(f"**Period**: {min(e["date"] for e in expenses)} – {max(e["date"] for e in expenses)}")
    lines.append(f"**Total Spend**: ${total_spend:,.2f}")
    lines.append(f"**Leverage Score** (top 3 categories): {leverage:.1f}%")
    lines.append("")
    lines.append("## Spend by Category")
    lines.append("
| Category | Amount |
|----------|--------|")
    for cat, amt in cat_totals.most_common():
        lines.append(f"| {cat} | ${amt:,.2f} |")
    lines.append("")
    lines.append("## Top 3 High‑Leverage Categories")
    for i, (cat, amt) in enumerate(top3, 1):
        lines.append(f"{i}. **{cat}** – ${amt:,.2f}")
    return "\n".join(lines)

def markdown_outliers(outliers: List[Dict[str, Any]]) -> str:
    if not outliers:
        return "# No outliers detected\n"
    lines = ["# Expense Outliers", ""]
    lines.append("| Date | Amount | Category | Description |")
    lines.append("|------|--------|----------|-------------|")
    for exp in outliers:
        lines.append(f"| {exp['date']} | ${exp['amount']:.2f} | {exp['category']} | {exp['description']} |")
    return "\n".join(lines)

# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="financial-leverage-analyzer", description="Detect high‑leverage spending patterns and outliers.")
    parser.add_argument("csv", type=Path, help="Path to expenses CSV file")
    parser.add_argument("-m", "--mapping", type=Path, default=Path("category_map.json"), help="JSON keyword→category map (optional)")
    sub = parser.add_subparsers(dest="command", required=True)
    sum_parser = sub.add_parser("summary", help="Print markdown summary")
    sum_parser.add_argument("-o", "--output", type=Path, help="Write summary to file (default stdout)")
    out_parser = sub.add_parser("outliers", help="Print markdown outlier list")
    out_parser.add_argument("-o", "--output", type=Path, help="Write outliers to file (default stdout)")
    out_parser.add_argument("-s", "--sigma", type=float, default=2.0, help="Sigma threshold for outlier detection")
    return parser

def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    expenses = load_expenses(args.csv)
    mapping = load_category_map(args.mapping)
    categorize(expenses, mapping)

    if args.command == "summary":
        md = markdown_summary(expenses)
        if args.output:
            args.output.write_text(md, encoding="utf-8")
        else:
            sys.stdout.write(md)
    elif args.command == "outliers":
        out = detect_outliers(expenses, sigma=args.sigma)
        md = markdown_outliers(out)
        if args.output:
            args.output.write_text(md, encoding="utf-8")
        else:
            sys.stdout.write(md)

if __name__ == "__main__":
    main()
