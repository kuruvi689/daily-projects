#!/usr/bin/env python3
"""loan-doc-summarizer
A tiny CLI that extracts key fields from a loan application document (PDF or plain text)
and prints a concise Markdown summary. Designed to run on CPU‑only Windows machines
with only the standard library and the ``requests`` package (used for optional
online validation via a free API).

Usage:
  python main.py <path-to-document>

The tool:
  * Accepts .txt or .pdf files (PDF is converted via ``pdfminer.six`` – optional).
  * Parses borrower name, email, phone, requested amount, purpose, and repayment
    term using regex patterns.
  * Validates email format locally and optionally checks MX records via a free
    DNS‑over‑HTTPS API.
  * Outputs a Markdown block that can be dropped into a SaaS dashboard or sent
    to a CRM.

The core parsing logic lives in ``extract_fields`` and is reusable in larger
systems (e.g., a FastAPI micro‑service)."""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Optional

# Optional PDF support – only import if the user has pdfminer.six installed.
# This keeps the base install lightweight; the CLI will still work for .txt.
try:
    from pdfminer.high_level import extract_text as pdf_extract_text
except ImportError:  # pragma: no cover
    pdf_extract_text = None

# Optional email MX validation via free DNS over HTTPS API.
# We use ``requests`` which is the only external dependency.
import requests

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{3,4}[\s-]?\d{4}\b")
AMOUNT_REGEX = re.compile(r"\b(?:Rs?|INR)\s?([\d,]+)\b", re.IGNORECASE)
TERM_REGEX = re.compile(r"\b(\d+)\s*(months?|years?)\b", re.IGNORECASE)
PURPOSE_REGEX = re.compile(r"Purpose[:\-]\s*(.+)", re.IGNORECASE)
NAME_REGEX = re.compile(r"Name[:\-]\s*([A-Za-z ,.'-]+)", re.IGNORECASE)


def read_document(path: Path) -> str:
    """Return the textual content of a .txt or .pdf file.
    If pdfminer is unavailable and a PDF is supplied, raise an informative error.
    """
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        if pdf_extract_text is None:
            raise RuntimeError(
                "pdfminer.six is not installed. Install it or use a .txt file."
            )
        return pdf_extract_text(str(path))
    raise ValueError("Unsupported file type. Use .txt or .pdf")


def extract_fields(text: str) -> Dict[str, Optional[str]]:
    """Extract known fields from free‑form loan application text.
    Returns a dict with keys: name, email, phone, amount, purpose, term.
    """
    result: Dict[str, Optional[str]] = {
        "name": None,
        "email": None,
        "phone": None,
        "amount": None,
        "purpose": None,
        "term": None,
    }
    # Simple line‑by‑line search for patterns.
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if not result["name"]:
            m = NAME_REGEX.search(line)
            if m:
                result["name"] = m.group(1).strip()
        if not result["email"]:
            m = EMAIL_REGEX.search(line)
            if m:
                result["email"] = m.group(0).strip()
        if not result["phone"]:
            m = PHONE_REGEX.search(line)
            if m:
                result["phone"] = m.group(0).strip()
        if not result["amount"]:
            m = AMOUNT_REGEX.search(line)
            if m:
                # Remove commas for readability.
                result["amount"] = m.group(1).replace(",", "")
        if not result["purpose"]:
            m = PURPOSE_REGEX.search(line)
            if m:
                result["purpose"] = m.group(1).strip()
        if not result["term"]:
            m = TERM_REGEX.search(line)
            if m:
                result["term"] = f"{m.group(1)} {m.group(2)}"
    return result


def validate_email_mx(email: str) -> bool:
    """Check if the domain of *email* has MX records using a free DNS‑over‑HTTPS API.
    Returns True if at least one MX record is found, False otherwise.
    """
    domain = email.split("@")[-1]
    url = f"https://cloudflare-dns.com/dns-query?name={domain}&type=MX"
    headers = {"accept": "application/dns-json"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return bool(data.get("Answer"))
    except Exception:
        return False


def markdown_summary(fields: Dict[str, Optional[str]]) -> str:
    """Create a Markdown summary from extracted fields."""
    lines = ["## Loan Application Summary", ""]
    for key in ["name", "email", "phone", "amount", "purpose", "term"]:
        val = fields.get(key) or "*not found*"
        lines.append(f"- **{key.title()}**: {val}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract key fields from a loan application document.")
    parser.add_argument("document", type=Path, help="Path to .txt or .pdf file")
    parser.add_argument("--validate-email", action="store_true", help="Perform MX lookup for extracted email")
    args = parser.parse_args()

    try:
        raw_text = read_document(args.document)
    except Exception as e:
        sys.exit(f"Error reading document: {e}")

    fields = extract_fields(raw_text)

    if args.validate_email and fields.get("email"):
        is_valid = validate_email_mx(fields["email"])
        fields["email"] += " (MX valid)" if is_valid else " (no MX)"

    print(markdown_summary(fields))


if __name__ == "__main__":
    main()
