#!/usr/bin/env python3
"""Prompt Optimizer CLI

A lightweight command‑line tool that analyses LLM prompts and suggests
improvements to make them more cost‑effective and higher‑quality.

Features
--------
- Token count using tiktoken (compatible with OpenAI, Groq, Claude models)
- Detects common issues: overly long context, missing system instruction,
  ambiguous placeholders, and excessive whitespace.
- Generates a concise Markdown report with actionable suggestions.
- Designed as a pure‑Python module that can be imported into larger SaaS
  back‑ends.

Usage
-----
    python main.py path/to/prompts.txt

The input file may contain one or multiple prompts separated by a line of
three dashes (`---`). Each prompt can optionally start with a `System:` line
followed by `User:` and `Assistant:` sections.

The tool runs on CPU‑only Windows machines and requires only the `tiktoken`
package.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

import tiktoken

# ---------- Helper Functions ----------

def load_prompts(file_path: Path) -> List[str]:
    """Read prompts from a file, split on lines containing only '---'."""
    content = file_path.read_text(encoding="utf-8")
    parts = [p.strip() for p in re.split(r"^---$", content, flags=re.MULTILINE) if p.strip()]
    return parts

def token_count(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Return token count for *text* using tiktoken encoding for *model*."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def parse_sections(prompt: str) -> Dict[str, str]:
    """Extract optional System, User, Assistant sections.
    Returns a dict with keys possibly missing.
    """
    sections = {}
    for label in ["System", "User", "Assistant"]:
        pattern = rf"^{label}:\s*(.*?)(?=^(?:System|User|Assistant):|\Z)"
        match = re.search(pattern, prompt, flags=re.DOTALL | re.MULTILINE)
        if match:
            sections[label.lower()] = match.group(1).strip()
    # Fallback: if no explicit labels, treat whole text as user prompt
    if not sections:
        sections["user"] = prompt.strip()
    return sections

def evaluate_prompt(sections: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Run heuristic checks. Returns (is_ok, list_of_issues)."""
    issues = []
    # 1. System instruction presence
    if "system" not in sections:
        issues.append("Missing System instruction – add a clear role for the model.")
    # 2. Token budget
    total_tokens = sum(token_count(v) for v in sections.values())
    if total_tokens > 800:
        issues.append(f"Prompt uses {total_tokens} tokens; consider trimming to ≤800 for cost efficiency.")
    # 3. Placeholder detection
    if re.search(r"\{\{.*?\}\}", " ".join(sections.values())):
        issues.append("Found unreplaced placeholders like {{variable}}.")
    # 4. Excessive whitespace / newlines
    if any(re.search(r"\n{3,}", v) for v in sections.values()):
        issues.append("Contains large blank blocks – collapse multiple newlines.")
    # 5. Very short user query
    user_len = len(sections.get("user", ""))
    if 0 < user_len < 20:
        issues.append("User prompt is very short; may be ambiguous.")
    return (len(issues) == 0, issues)

def generate_report(prompt_idx: int, sections: Dict[str, str], ok: bool, issues: List[str]) -> str:
    """Create a markdown snippet for one prompt."""
    header = f"## Prompt {prompt_idx + 1}\n"
    meta = []
    for role, text in sections.items():
        meta.append(f"**{role.title()}** ({token_count(text)} tokens):\n```
{text}
```\n")
    status = "✅ Good to go" if ok else "⚠️ Issues detected"
    issue_md = "".join([f"- {i}\n" for i in issues])
    return header + "\n".join(meta) + f"\n**Overall:** {status}\n\n" + (f"**Suggestions:**\n{issue_md}\n" if issues else "")

# ---------- Main CLI ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze LLM prompts and suggest optimizations.")
    parser.add_argument("input", type=Path, help="Path to a .txt file containing one or more prompts.")
    parser.add_argument("-o", "--output", type=Path, default=Path("prompt_report.md"), help="File to write the markdown report.")
    args = parser.parse_args()

    if not args.input.is_file():
        sys.exit(f"Error: {args.input} does not exist or is not a file.")

    prompts = load_prompts(args.input)
    reports: List[str] = []
    for idx, prompt in enumerate(prompts):
        sections = parse_sections(prompt)
        ok, issues = evaluate_prompt(sections)
        reports.append(generate_report(idx, sections, ok, issues))

    full_report = "# Prompt Optimization Report\n\n" + "\n---\n\n".join(reports)
    args.output.write_text(full_report, encoding="utf-8")
    print(f"Report written to {args.output}")

if __name__ == "__main__":
    main()
