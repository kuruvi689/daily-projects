import csv
import argparse
import sys
from pathlib import Path
from string import Template

def load_template(path: Path) -> Template:
    """Load email template file and return a Template object.
    The template can use $field placeholders matching CSV column names.
    """
    try:
        content = path.read_text(encoding="utf-8")
        return Template(content)
    except Exception as e:
        sys.stderr.write(f"Error reading template: {e}\n")
        sys.exit(1)

def read_leads(csv_path: Path) -> list[dict[str, str]]:
    """Read leads CSV and return list of dict rows.
    Expected first row to be header with column names.
    """
    try:
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except Exception as e:
        sys.stderr.write(f"Error reading CSV: {e}\n")
        sys.exit(1)

def generate_emails(leads: list[dict[str, str]], tmpl: Template) -> list[str]:
    emails = []
    for lead in leads:
        try:
            email = tmpl.substitute(**lead)
        except KeyError as missing:
            sys.stderr.write(
                f"Missing placeholder {missing} for lead {lead.get('email', 'unknown')}\n"
            )
            email = ""
        emails.append(email)
    return emails

def write_output(emails: list[str], out_path: Path | None):
    content = "\n---\n".join(email for email in emails if email)
    if out_path:
        out_path.write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate personalized lead emails from a CSV and a template."
    )
    parser.add_argument(
        "csv_file", type=Path, help="Path to leads CSV file (must contain header row)"
    )
    parser.add_argument(
        "template_file", type=Path, help="Path to email template file using $placeholders"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write result to file; default prints to stdout",
    )
    args = parser.parse_args()

    if not args.csv_file.is_file():
        sys.stderr.write(f"CSV file not found: {args.csv_file}\n")
        sys.exit(1)
    if not args.template_file.is_file():
        sys.stderr.write(f"Template file not found: {args.template_file}\n")
        sys.exit(1)

    tmpl = load_template(args.template_file)
    leads = read_leads(args.csv_file)
    if not leads:
        sys.stderr.write("No leads found in CSV.\n")
        sys.exit(0)

    emails = generate_emails(leads, tmpl)
    write_output(emails, args.output)

if __name__ == "__main__":
    main()
