# loan-lead-optimizer

A tiny, **CPU‑only** Python CLI that scores and ranks small‑business loan leads for Suryoday Bank (or any fintech). It turns a raw CSV of prospects into a prioritized JSON list, helping sales teams focus on the highest‑potential borrowers.

---

## 🎯 Aim
- **Financial Independence** – accelerate revenue by turning lead‑gen data into actionable insight.
- **Micro‑SaaS ready** – can be packaged as a $5‑20/month service (upload CSV, get ranked leads).
- **Modular** – core scoring logic (`score_lead`) is a pure function, easy to import into larger pipelines (e.g., n8n workflows, Flask APIs).

---

## 🚀 Quick Start
```bash
# Clone & install (no external deps)
git clone https://github.com/yourname/loan-lead-optimizer.git
cd loan-lead-optimizer
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt  # empty for stdlib only

# Run the CLI
python main.py leads.csv --top 5
```

- `leads.csv` must contain columns: `name,email,phone,annual_revenue,credit_score,existing_loans`.
- Output JSON (`scored_leads.json` by default) contains the original rows plus a `score` field (0‑100).

---

## 📦 Usage
```bash
python main.py <input_csv> [options]

Options:
  -o, --output PATH   Path to write scored JSON (default: scored_leads.json)
  -t, --top INT       Number of top leads to print to console (default: 10)
```

---

## 🛠️ How It Works
1. **Parse CSV** – validates required columns and converts numeric fields.
2. **Score** – simple weighted model:
   - Revenue (0‑1M+) → 40 %
   - Credit score (0‑900) → 40 %
   - Existing loans (0‑10+) → -20 %
3. **Rank** – descending sort by score.
4. **Export** – JSON for downstream consumption (CRM, n8n, Airtable, etc.).

The model is deliberately lightweight; you can replace the `score_lead` function with a ML model later without touching the CLI.

---

## 📈 Business Model
- **Tier 1 ($5/mo)** – CSV upload via a tiny Flask API, returns ranked JSON.
- **Tier 2 ($15/mo)** – Adds custom weight configuration per client.
- **Tier 3 ($20/mo)** – Daily automated scoring via a scheduled Railway job, email report.

All tiers run on free‑tier Railway or Railway‑Lite containers (CPU‑only).

---

## 🏷️ Tags
#AIMastery #Strategy #Finance

---

## License
MIT – feel free to fork, extend, and sell as a service.
