import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime

def parse_actions(text: str):
    """Extract action items from raw meeting notes.
    Expected format (case‑insensitive):
        - [action] Owner: @username Due: YYYY-MM-DD
    Anything that matches the pattern is returned as a dict.
    """
    pattern = re.compile(
        r"[-*]\s*(?P<action>.+?)\s+Owner:\s*@?(?P<owner>\w+)\s+Due:\s*(?P<due>\d{4}-\d{2}-\d{2})",
        re.IGNORECASE,
    )
    actions = []
    for m in pattern.finditer(text):
        action = m.group('action').strip()
        owner = m.group('owner').strip()
        due_str = m.group('due')
        try:
            due = datetime.strptime(due_str, "%Y-%m-%d").date().isoformat()
        except ValueError:
            due = due_str  # keep raw if unparsable
        actions.append({"action": action, "owner": owner, "due": due})
    return actions

def generate_markdown(actions):
    if not actions:
        return "*No action items found.*\n"
    lines = ["# Action Items\n"]
    for idx, a in enumerate(actions, 1):
        lines.append(f"{idx}. **{a['action']}**  ")
        lines.append(f"   - Owner: @{a['owner']}  ")
        lines.append(f"   - Due: {a['due']}\n")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Parse meeting notes and extract action items into a markdown task list."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the meeting notes file (plain text or markdown).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write markdown to this file; otherwise prints to stdout.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also output raw JSON to stdout (useful for API integration).",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        sys.stderr.write(f"Error: {args.input} does not exist or is not a file.\n")
        sys.exit(1)

    text = args.input.read_text(encoding="utf-8")
    actions = parse_actions(text)

    markdown = generate_markdown(actions)
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        print(f"✅ Action list written to {args.output}")
    else:
        print(markdown)

    if args.json:
        json.dump(actions, sys.stdout, indent=2)
        print()  # newline after JSON

if __name__ == "__main__":
    main()
