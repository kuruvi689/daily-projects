# loan-doc-summarizer

A lightweight **Python CLI** that parses loan‑application documents (plain‑text or PDF) and produces a concise Markdown summary. Ideal as a micro‑service for fintech SaaS platforms (e.g., a $5‑20/month add‑on for lead‑gen pipelines).

## Features
- **Zero‑GPU, CPU‑only** – runs on any Windows machine.
- Supports `.txt` out‑of‑the‑box; optional PDF support via `pdfminer.six`.
- Extracts: borrower name, email, phone, requested amount, purpose, repayment term.
- Optional MX‑record validation for emails using a free Cloudflare DNS‑over‑HTTPS API.
- Core parsing logic (`extract_fields`) is modular and can be imported into larger
  systems (FastAPI, n8n, etc.).

## Installation
```bash
pip install -r requirements.txt   # only "requests" is required; pdfminer.six optional
```

## Usage
```bash
python main.py path/to/application.txt          # plain text
python main.py path/to/application.pdf           # PDF (requires pdfminer.six)
python main.py path/to/application.txt --validate-email   # MX lookup
```

The CLI prints a Markdown block:
```markdown
## Loan Application Summary
- **Name**: Jane Doe
- **Email**: jane@example.com (MX valid)
- **Phone**: +91 98765 43210
- **Amount**: 500000
- **Purpose**: Expand bakery operations
- **Term**: 12 months
```

## Extending the Tool
- **Import `extract_fields`** in other Python projects to reuse the parsing logic.
- Wrap the CLI in a FastAPI endpoint for a true SaaS offering.
- Add more regex patterns for additional fields (e.g., collateral details).

## License
MIT – free for commercial use.

#AIMastery #Strategy #Finance
