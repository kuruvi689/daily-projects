import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

TEMPLATE_DIR = Path(__file__).parent / "templates"
DEFAULT_TEMPLATE = "default.txt"

def load_template(name: str) -> str:
    """Load an email template.
    If the file does not exist, fall back to the built‑in default.
    """
    path = TEMPLATE_DIR / name
    if path.is_file():
        return path.read_text(encoding="utf-8")
    # built‑in fallback
    return (
        "Subject: Quick follow‑up on your loan inquiry\n\n"
        "Hi {{first_name}},\n\n"
        "Thank you for your interest in a {{loan_type}} loan with Suryoday Bank. "
        "Based on the information you provided, you may be eligible for a loan amount of up to {{max_amount}} INR. "
        "We'd love to discuss the next steps and answer any questions you have.\n\n"
        "Best regards,\n"
        "{{agent_name}}\n"
        "Suryoday Small Finance Bank"
    )

def render_template(template: str, data: Dict[str, str]) -> str:
    """Very small placeholder replacement engine.
    Uses {{key}} syntax. Missing keys are left unchanged.
    """
    def repl(match: re.Match) -> str:
        key = match.group(1).strip()
        return data.get(key, match.group(0))
    return re.sub(r"{{\s*(.*?)\s*}}", repl, template)

def parse_leads(file_path: Path) -> List[Dict[str, str]]:
    """Parse a JSONL (one JSON object per line) lead file.
    Expected fields: first_name, last_name, email, loan_type, max_amount, agent_name (optional)
    """
    leads = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                leads.append(obj)
            except json.JSONDecodeError as e:
                print(f"Skipping malformed line: {e}", file=sys.stderr)
    return leads

def generate_emails(leads: List[Dict[str, str]], template_name: str) -> List[Tuple[str, str]]:
    """Return a list of (email, rendered_message) tuples.
    The email address is taken from the lead dict; if missing, the entry is skipped.
    """
    tmpl = load_template(template_name)
    results = []
    for lead in leads:
        email = lead.get("email")
        if not email:
            continue
        rendered = render_template(tmpl, lead)
        results.append((email, rendered))
    return results

def write_output(pairs: List[Tuple[str, str]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, (email, body) in enumerate(pairs, 1):
        safe_email = re.sub(r"[^a-zA-Z0-9_.@-]", "_", email)
        file_path = out_dir / f"{idx}_{safe_email}.txt"
        file_path.write_text(body, encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate personalized loan‑lead follow‑up emails from a JSONL lead list."
    )
    parser.add_argument(
        "lead_file",
        type=Path,
        help="Path to a JSONL file where each line is a lead record."
    )
    parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE,
        help="Template file name placed in ./templates (default built‑in)."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("generated-emails"),
        help="Directory where rendered emails will be written."
    )
    args = parser.parse_args()

    if not args.lead_file.is_file():
        print(f"Lead file not found: {args.lead_file}", file=sys.stderr)
        sys.exit(1)

    leads = parse_leads(args.lead_file)
    if not leads:
        print("No valid leads found.", file=sys.stderr)
        sys.exit(1)

    pairs = generate_emails(leads, args.template)
    if not pairs:
        print("No emails generated – check that leads contain an 'email' field.", file=sys.stderr)
        sys.exit(1)

    write_output(pairs, args.out_dir)
    print(f"Generated {len(pairs)} emails in {args.out_dir}")

if __name__ == "__main__":
    main()
