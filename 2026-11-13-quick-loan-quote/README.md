# quick-loan-quote

**Tag:** #AIMastery #Strategy #Finance

## Overview
`quick-loan-quote` is a tiny Python CLI that instantly produces a provisional loan eligibility
quote for Suryoday Small Finance Bank’s unsecured business loans. It ingests a few key
business metrics, runs a lightweight rule‑based scoring model, and returns:
- An eligibility score (0‑100)
- A maximum loan amount estimate
- A suggested interest rate

The tool is designed to be **SaaS‑ready** – wrap the CLI in a tiny HTTP endpoint or
schedule it via n8n to offer a $5‑20 /month micro‑service for loan officers or
founders who need rapid pre‑qualification.

## Features
- **Zero‑dependency** – pure stdlib, runs on any Windows CPU‑only machine.
- Interactive prompts *or* command‑line flags for automation.
- Markdown report for human consumption and a JSON file for programmatic use.
- Extensible scoring logic that can be imported into larger pipelines.

## Installation
```bash
# Clone the repo and run the CLI (Python 3.9+ required)
git clone https://github.com/yourname/quick-loan-quote.git
cd quick-loan-quote
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r requirements.txt  # currently empty
```

## Usage
### Interactive mode
```bash
python main.py
```
The script will ask for:
- Annual revenue (INR)
- Business age (years)
- Credit score (300‑900)
- Existing debt (INR)

### Direct arguments (ideal for automation)
```bash
python main.py --revenue 1500000 --tenure 4 --credit 750 --debt 250000 --output quote.md
```

The markdown report is saved to `quote.md` and a machine‑readable `quote.json`
appears alongside it.

## Extending / Embedding
The core functions (`eligibility_score`, `generate_report`) are importable:
```python
from main import eligibility_score, generate_report
```
You can call them from a FastAPI endpoint, an n8n workflow, or any other
Python‑based SaaS stack.

## Pricing Model (for SaaS)
- **Free tier:** 10 quotes per month (rate‑limited).
- **Pro tier ($9/mo):** Unlimited quotes, custom scoring parameters, webhook
  callbacks.
- **Enterprise ($19/mo):** White‑label branding, audit logs, SLA support.

## License
MIT – free for commercial use.

---
*Built for Suryoday Bank lead‑generation automation and personal financial independence.*
