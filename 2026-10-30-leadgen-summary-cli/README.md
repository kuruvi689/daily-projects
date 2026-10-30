# LeadGen Summary CLI

A lightweight, CPU‑only command‑line tool that turns raw lead‑generation CSV dumps into ready‑to‑publish JSON summaries. Perfect for micro‑SaaS dashboards, weekly newsletters, or automated reporting pipelines.

## Features
- **Period aggregation** – daily, weekly, or monthly summaries.
- **Key metrics** – total leads, total amount, breakdown by source and status.
- **Zero‑dependency** – built entirely on Python’s standard library, ideal for Windows machines without a GPU.
- **SaaS‑ready** – expose the JSON via a tiny FastAPI wrapper later, or ship as a $5‑20/month service.
- **Modular** – core functions (`read_csv`, `aggregate`, `bucket_date`) are importable for larger systems.

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r requirements.txt  # (empty – stdlib only)
```

## Usage
```bash
python main.py --input leads.csv --period weekly --output summary.json
```
- `leads.csv` must contain the columns: `date,source,category,amount,status`.
- Dates are ISO‑format (`YYYY‑MM‑DD`).
- `--output -` prints the JSON to stdout.

## Example CSV
```csv
date,source,category,amount,status
2026-10-01,Facebook,SME,1200,qualified
2026-10-02,LinkedIn,Enterprise,5000,contacted
2026-10-03,Referral,SME,800,won
```

## Example Output (weekly)
```json
{
  "2026-W40": {
    "amount": 7000.0,
    "by_source": {
      "Facebook": 1,
      "LinkedIn": 1,
      "Referral": 1
    },
    "by_status": {
      "qualified": 1,
      "contacted": 1,
      "won": 1
    },
    "leads": 3
  }
}
```

## Extending the Tool
- Wrap `main()` in a FastAPI endpoint for a REST micro‑service.
- Add email or Slack hooks to push the summary automatically.
- Persist raw rows in a SQLite DB for historical analytics.

## License
MIT – free for commercial use.

---
#AIMastery #Strategy #Finance
