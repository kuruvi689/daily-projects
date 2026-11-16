# loan-eligibility-cli

A lightweight Python CLI that scores small‑business loan leads for **Suryoday Bank** and suggests the next action. Perfect as a standalone micro‑service ($5‑20 /mo) or as a building block in larger automation pipelines.

---

## Features
- **Zero‑dependency** (standard library only) – runs on any CPU‑only Windows box.
- Reads a CSV of leads with columns `lead_id, turnover, credit_score, business_tenure_months`.
- Configurable eligibility thresholds via command‑line flags.
- Outputs a JSON array containing:
  - `lead_id`
  - `eligible` (bool)
  - `score` (0‑1 confidence)
  - `action` (`fast‑track`, `standard review`, `reject`).
- Core scoring logic (`evaluate_lead`) is isolated for reuse in SaaS back‑ends, n8n flows, or Google Cloud Functions.

---

## Quick Start
```bash
# Clone & run (requires Python 3.9+)
git clone https://github.com/yourname/loan-eligibility-cli.git
cd loan-eligibility-cli
python main.py --input leads.csv --output results.json
```

### Custom thresholds
```bash
python main.py \
  --input leads.csv \
  --min-turnover 750000 \
  --min-credit 700 \
  --min-tenure 18
```

---

## Integration Ideas (#AIMastery #Strategy #Finance)
- **n8n node**: call the CLI from an n8n workflow to auto‑tag incoming leads.
- **SaaS wrapper**: expose the `evaluate_lead` function via FastAPI; charge per month for API access.
- **Dashboard**: feed the JSON into a cheap Vercel static site for real‑time lead health.

---

## License
MIT – free for personal and commercial use.
