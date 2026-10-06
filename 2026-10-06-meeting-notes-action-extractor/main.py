import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime

ACTION_PATTERN = re.compile(
    r"(?P<bullet>[-*•])?\s*(?P<action>.+?)(?:\s+\(?(?P<owner>@?\w+)?\)?)?\s*(?:by\s+(?P<date>\d{4}[-/]\d{2}[-/]\d{2}|today|tomorrow|next week))?",
    re.IGNORECASE,
)

DATE_KEYWORDS = {
    "today": lambda: datetime.today().strftime("%Y-%m-%d"),
    "tomorrow": lambda: (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
    "next week": lambda: (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
}

def parse_line(line: str) -> dict | None:
    m = ACTION_PATTERN.search(line)
    if not m:
        return None
    action = m.group('action').strip()
    owner = m.group('owner')
    raw_date = m.group('date')
    if raw_date:
        raw_date = raw_date.strip().lower()
        if raw_date in DATE_KEYWORDS:
            due = DATE_KEYWORDS[raw_date]()
        else:
            due = raw_date.replace('/', '-')
    else:
        due = None
    return {
        "action": action,
        "owner": owner if owner else "",
        "due": due if due else "",
    }

def extract_actions(text: str) -> list[dict]:
    actions = []
    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            actions.append(parsed)
    return actions

def format_markdown(actions: list[dict]) -> str:
    lines = ["# Action Items\n"]
    for i, a in enumerate(actions, 1):
        owner = f"@{a['owner']}" if a['owner'] else ""
        due = f"(due: {a['due']})" if a['due'] else ""
        lines.append(f"- [{i}] {a['action']} {owner} {due}")
    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract action items from meeting notes and output a markdown task list."
    )
    parser.add_argument("input", type=Path, help="Path to meeting notes text file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write markdown to file; otherwise prints to stdout",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        sys.exit(f"Error: input file '{args.input}' not found.")

    text = args.input.read_text(encoding="utf-8")
    actions = extract_actions(text)

    if not actions:
        sys.exit("No action items detected.")

    markdown = format_markdown(actions)

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        print(f"✅ Action list written to {args.output}")
    else:
        print(markdown)

if __name__ == "__main__":
    main()
