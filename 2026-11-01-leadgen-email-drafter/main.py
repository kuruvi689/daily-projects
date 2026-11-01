# main.py
"""leadgen-email-drafter
A tiny CLI to generate personalized outreach emails for loan‑lead lists.

Usage:
  python main.py leads.csv template.txt output_dir/

- leads.csv : header row with at least `name,email` and any extra columns.
- template.txt : email body with Jinja2 placeholders, e.g. {{ name }}, {{ company }}.
- output_dir : directory where one .txt file per lead will be written.

The tool is pure Python + Jinja2, runs on any CPU‑only Windows box and can be
exposed as a micro‑service (e.g. FastAPI wrapper) for a $5‑20/month SaaS.
"""

import sys
import os
import csv
from pathlib import Path
from typing import List, Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError


def load_leads(csv_path: Path) -> List[Dict[str, str]]:
    """Read CSV and return a list of dict rows.
    Empty rows are ignored. All values are stripped.
    """
    leads = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {k: (v or "").strip() for k, v in row.items()}
            if cleaned.get("email"):
                leads.append(cleaned)
    return leads


def load_template(template_path: Path) -> str:
    """Return raw template string."""
    return template_path.read_text(encoding="utf-8")


def render_email(template_str: str, context: Dict[str, str]) -> str:
    env = Environment(loader=FileSystemLoader("/"), undefined=StrictUndefined)
    try:
        tmpl = env.from_string(template_str)
        return tmpl.render(**context)
    except TemplateError as e:
        raise RuntimeError(f"Template rendering failed: {e}")


def write_email(output_dir: Path, lead: Dict[str, str], content: str) -> None:
    safe_name = "_".join(lead.get("name", "lead").split()).lower()
    filename = f"{safe_name}_{lead.get('email', 'noemail')}.txt"
    out_path = output_dir / filename
    out_path.write_text(content, encoding="utf-8")


def main(argv: List[str] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 3:
        print("Usage: python main.py <leads.csv> <template.txt> <output_dir>")
        sys.exit(1)

    csv_path = Path(argv[0])
    tmpl_path = Path(argv[1])
    out_dir = Path(argv[2])

    if not csv_path.is_file():
        print(f"Leads file not found: {csv_path}")
        sys.exit(1)
    if not tmpl_path.is_file():
        print(f"Template file not found: {tmpl_path}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    leads = load_leads(csv_path)
    if not leads:
        print("No leads with email found in CSV.")
        sys.exit(0)

    template_str = load_template(tmpl_path)

    for lead in leads:
        try:
            email_body = render_email(template_str, lead)
            write_email(out_dir, lead, email_body)
        except RuntimeError as e:
            print(f"Skipping {lead.get('email')}: {e}")

    print(f"Generated {len(leads)} emails in {out_dir}")


if __name__ == "__main__":
    main()
