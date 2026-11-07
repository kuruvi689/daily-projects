import csv
import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict

def load_leads(file_path: Path):
    """Load leads from a CSV file. Expected columns: name,email,phone,source"""
    leads = []
    with file_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append({
                "name": row.get("name", "").strip(),
                "email": row.get("email", "").strip().lower(),
                "phone": row.get("phone", "").strip(),
                "source": row.get("source", "").strip(),
            })
    return leads

def normalize_phone(phone: str) -> str:
    # Remove non‑digit characters, keep last 10 digits (Indian numbers)
    digits = "".join(filter(str.isdigit, phone))
    return digits[-10:] if len(digits) >= 10 else digits

def deduplicate(leads):
    """Deduplicate leads using email and phone as keys.
    Returns a list of unique leads and a report dict.
    """
    seen = {}
    duplicates = []
    for lead in leads:
        email_key = lead["email"]
        phone_key = normalize_phone(lead["phone"]) if lead["phone"] else ""
        key = email_key or phone_key
        if not key:
            # No reliable identifier – keep as is but mark
            duplicates.append({"lead": lead, "reason": "no identifier"})
            continue
        if key in seen:
            # Merge source info
            existing = seen[key]
            existing["source"] = ", ".join(sorted(set(existing["source"].split(", ") + [lead["source"]])))
            duplicates.append({"lead": lead, "reason": "duplicate of " + existing["name"]})
        else:
            seen[key] = lead
    unique = list(seen.values())
    report = {
        "total": len(leads),
        "unique": len(unique),
        "duplicates": len(duplicates),
    }
    return unique, duplicates, report

def write_output(unique, duplicates, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Unique leads CSV
    uniq_path = out_dir / "unique_leads.csv"
    if unique:
        with uniq_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "email", "phone", "source"])
            writer.writeheader()
            writer.writerows(unique)
    # Duplicates JSON for audit
    dup_path = out_dir / "duplicates.json"
    with dup_path.open("w", encoding="utf-8") as f:
        json.dump(duplicates, f, indent=2)
    return uniq_path, dup_path

def print_report(report):
    print("--- Deduplication Report ---")
    print(f"Total processed : {report['total']}")
    print(f"Unique leads    : {report['unique']}")
    print(f"Duplicates found: {report['duplicates']}")
    print("----------------------------")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Deduplicate loan lead CSVs for Suryoday Bank – a lightweight, SaaS‑ready CLI tool.")
    parser.add_argument("input", type=Path, help="Path to input CSV containing raw leads")
    parser.add_argument("--out", type=Path, default=Path("./deduped"), help="Directory for output files")
    parser.add_argument("--json", action="store_true", help="Print detailed duplicate report as JSON to stdout")
    return parser.parse_args()

def main():
    args = parse_args()
    if not args.input.is_file():
        print(f"Error: input file {args.input} does not exist", file=sys.stderr)
        sys.exit(1)
    leads = load_leads(args.input)
    unique, duplicates, report = deduplicate(leads)
    uniq_path, dup_path = write_output(unique, duplicates, args.out)
    print_report(report)
    print(f"Unique leads written to: {uniq_path}")
    print(f"Duplicate audit written to: {dup_path}")
    if args.json:
        print("\nDetailed duplicate list (JSON):")
        print(json.dumps(duplicates, indent=2))

if __name__ == "__main__":
    main()
