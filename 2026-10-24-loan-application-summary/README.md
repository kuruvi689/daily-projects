# Loan Application Summary CLI

A lightweight, CPU‑only Python CLI that ingests raw loan‑application CSVs, sanitises contact data, aggregates key metrics and exports **ready‑to‑use JSON** and **cleaned CSV** files. Perfect as a micro‑SaaS offering for fintechs, lead‑gen teams, or anyone needing a quick, privacy‑first summary of loan pipelines.

---

## Features
- **Zero‑dependency** (standard library only) – runs on any Windows machine.
- Parses common date formats and monetary strings.
- Light email validation & phone normalisation.
- Monthly breakdown of applications, approvals, rejections, and pending status.
- Generates a concise JSON summary and an optional cleaned CSV for downstream workflows.
- CLI‑first design; can be wrapped by n8n, Railway, or any automation layer.

---

## Installation
```bash
# Clone the repo (or copy main.py) and install (no extra packages needed)
python -m venv .venv
.venv\Scripts\activate
# No pip packages required – only stdlib
```

---

## Usage
```bash
python main.py path/to/applications.csv [--out-dir ./output] [--no-clean]
```
- `--out-dir` – Destination folder for `summary.json` and `cleaned_applications.csv`.
- `--no-clean` – Skip CSV export if you only need the JSON summary.

---

## Sample Input CSV
| applicant_name | email               | phone          | loan_amount | application_date | status   |
|----------------|---------------------|----------------|------------|------------------|----------|
| Jane Doe       | jane@example.com    | +91 98765 4321 | $5,000      | 2024-09-15       | approved |
| John Smith     | john[at]mail.com    | 1234567890     | 12000      | 15/09/2024       | pending  |

---

## Output
- **summary.json** – machine‑readable aggregation.
- **cleaned_applications.csv** – ready for import into CRM or analytics tools.

---

## SaaS Angle
Package this as a hosted endpoint (Railway, Railway‑Lite) that accepts a CSV upload, runs the CLI in a container, and returns the JSON payload. Pricing at $5‑$20 / month per 10 k rows is feasible given the negligible compute cost.

---

## Tags
#AIMastery #Strategy #Finance

---

## License
MIT – free for personal and commercial use.
