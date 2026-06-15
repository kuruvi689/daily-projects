"""Habit Streak Tracker: a small daily Python portfolio project."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_records(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list of records.")
    return data


def summarize(records: list[dict[str, object]]) -> dict[str, object]:
    categories = Counter(str(record.get("category", "uncategorized")) for record in records)
    total_score = sum(float(record.get("score", 0)) for record in records)
    flagged = [record for record in records if bool(record.get("flagged", False))]
    return {
        "project": "Habit Streak Tracker",
        "records": len(records),
        "categories": dict(categories),
        "total_score": round(total_score, 2),
        "flagged_records": len(flagged),
    }


def print_summary(summary: dict[str, object]) -> None:
    print(f"{summary['project']}")
    print(f"Records analyzed: {summary['records']}")
    print(f"Total score: {summary['total_score']}")
    print(f"Flagged records: {summary['flagged_records']}")
    print("Categories:")
    for name, count in sorted(summary["categories"].items()):
        print(f"  - {name}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Records daily habit completions and reports streaks, completion rate, and missed days.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).with_name("sample_data.json"),
        help="Path to a JSON list of records.",
    )
    args = parser.parse_args()
    print_summary(summarize(load_records(args.input)))


if __name__ == "__main__":
    main()
