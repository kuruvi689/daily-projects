import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$")

def load_contacts(path: Path) -> List[Dict[str, str]]:
    """Load contacts from a CSV or JSON file.
    Expected columns/keys: name, email, phone, company (optional).
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    elif path.suffix.lower() == ".json":
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            raise ValueError("JSON must contain a list of objects")
    else:
        raise ValueError("Supported input formats: .csv, .json")

def is_valid_email(email: str) -> bool:
    """Very lightweight email validation using regex.
    It does not check MX records – keeping it CPU‑only and free.
    """
    return bool(EMAIL_REGEX.fullmatch(email.strip()))

def dedupe_contacts(contacts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate emails, keeping the first occurrence.
    Returns a new list preserving order.
    """
    seen = set()
    unique = []
    for c in contacts:
        email = c.get("email", "").strip().lower()
        if email and email not in seen:
            seen.add(email)
            unique.append(c)
    return unique

def sanitize_contacts(contacts: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Separate valid and invalid contacts.
    Returns (valid, invalid).
    """
    valid, invalid = [], []
    for c in contacts:
        email = c.get("email", "").strip()
        if is_valid_email(email):
            valid.append(c)
        else:
            invalid.append(c)
    return valid, invalid

def export_csv(contacts: List[Dict[str, str]], path: Path) -> None:
    if not contacts:
        return
    fieldnames = contacts[0].keys()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)

def export_json(contacts: List[Dict[str, str]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

def summary(valid: List[Dict[str, str]], invalid: List[Dict[str, str]]) -> str:
    total = len(valid) + len(invalid)
    return (
        f"Processed {total} contacts.\n"
        f"✅ Valid emails: {len(valid)}\n"
        f"❌ Invalid emails: {len(invalid)}"
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sanitize lead‑generation contact lists – validate emails, dedupe, and export clean data."
    )
    parser.add_argument("input", type=Path, help="Path to input CSV or JSON file.")
    parser.add_argument("--out-dir", type=Path, default=Path("./output"), help="Directory for cleaned files.")
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Export format for the cleaned list (default: csv).",
    )
    parser.add_argument(
        "--keep-invalid",
        action="store_true",
        help="Also export a file with invalid contacts for manual review.",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    contacts = load_contacts(args.input)
    contacts = dedupe_contacts(contacts)
    valid, invalid = sanitize_contacts(contacts)

    clean_path = args.out_dir / f"clean_contacts.{args.format}"
    if args.format == "csv":
        export_csv(valid, clean_path)
    else:
        export_json(valid, clean_path)

    if args.keep_invalid:
        invalid_path = args.out_dir / f"invalid_contacts.{args.format}"
        if args.format == "csv":
            export_csv(invalid, invalid_path)
        else:
            export_json(invalid, invalid_path)

    print(summary(valid, invalid))
    print(f"✅ Clean file written to {clean_path}")
    if args.keep_invalid:
        print(f"⚠️ Invalid file written to {invalid_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
