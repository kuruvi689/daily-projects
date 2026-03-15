# LLM Response Quality Analyzer

**Goal Area:** AI & Automation Mastery  
**Date:** 2026-03-15  
**Complexity:** Intermediate  

## What It Does
This tool evaluates text responses from Large Language Models against a set of quality metrics. it calculates readability scores (Flesch-Kincaid), validates JSON structure within markdown, monitors keyword presence, and estimates sentiment.

## Why It Exists
In high-stakes AI automation, ensuring that a model's output is readable, contains the correct information, and follows specific formats (like JSON) is critical for system reliability.

## How to Use
```bash
pip install -r requirements.txt
python main.py
```

## Example Output
```text
──────────────────────── LLM Response Quality Analysis ─────────────────────────
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Metric            ┃ Value           ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Word Count        │ 42              │
│ Readability Score │ 62.41           │
│ Reading Ease      │ Standard        │
│ Sentiment         │ Positive        │
│ JSON Valid        │ ✅              │
└───────────────────┴─────────────────┘

Keyword Checklist:
 • portfolio: Found
 • JSON: Found
 • stocks: Found
 • risk: Missing
```

## Key Features
- **Readability Scoring:** Uses the Flesch Reading Ease algorithm via `textstat`.
- **JSON Extraction:** Automatically finds and validates JSON blocks within Markdown.
- **Keyword Monitoring:** Ensures specific domain terms are present (or flags them as missing).
- **Rich Visualization:** Uses the `rich` library for beautiful terminal reporting.

## Future Improvements
- [ ] Add integration with GPT-4 for semantic correctness checking.
- [ ] Implement support for custom regex-based validation rules.
- [ ] Add CSV export for batch processing of responses.

## Technical Details
**Language:** Python 3.11+  
**Dependencies:** textstat, rich  
**Time to Build:** 45 minutes  

---
*Part of daily project series - Building toward AI mastery and technical excellence*
