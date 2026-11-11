# LeadGen Performance Dashboard

A tiny, CPU‑only Python CLI that turns a raw lead‑generation CSV export into a ready‑to‑sell SaaS‑style JSON dashboard.

---

## 🎯 Aim
* **Category**: #AIMastery / #Strategy / #Finance
* **Problem**: Small businesses and fintech founders (like Sivanesh) need instant visibility into lead quality, source ROI, and conversion rates without building a full analytics stack.
* **Solution**: Upload a CSV (exported from any CRM) and receive a concise JSON report that can be fed into a micro‑service, displayed on a dashboard, or emailed to stakeholders.

---

## ✨ Features
- **Zero‑dependency** – pure standard‑library implementation (works on any Windows CPU‑only machine).
- Automatic aggregation of:
  - Total leads, date range, status & source breakdowns.
  - Revenue per status/source.
  - Conversion rate (won / total).
- Configurable date format (`--date-format`).
- Outputs both a `dashboard.json` file **and** a pretty‑printed console view.
- Designed as a **modular core** (`aggregate`) that can be imported by larger SaaS back‑ends.

---

## 📦 Installation
```bash
# Clone the repo (or copy the single file)
git clone https://github.com/yourname/leadgen-performance-dashboard.git
cd leadgen-performance-dashboard
# No external packages needed
python -m pip install --upgrade pip
```

---

## 🚀 Usage
```bash
python main.py path/to/leads.csv [--output dashboard.json] [--date-format "%Y-%m-%d"]
```
### Expected CSV columns
| Column | Description |
|--------|-------------|
| `id` | Unique lead identifier |
| `source` | Where the lead originated (e.g., facebook, referral) |
| `created_at` | Date the lead was created |
| `status` | Current status (e.g., new, contacted, won, lost) |
| `amount` | Potential revenue (numeric) |

---

## 🔧 Extending the Core
The `aggregate(rows, date_fmt)` function returns a plain Python dict. Import it in another project to combine with FastAPI, Flask, or n8n workflows:
```python
from main import read_csv, aggregate
rows = read_csv('leads.csv')
report = aggregate(rows, '%Y-%m-%d')
# send `report` to your SaaS backend
```

---

## 💰 SaaS‑ready Pricing Idea
- **Free tier**: up to 1 000 rows/month.
- **Pro tier ($9/mo)**: unlimited rows, custom date formats, webhook integration.
- Host on Railway or Vercel as a tiny HTTP wrapper around the core logic.

---

## 🛡️ License
MIT – free for personal and commercial use.
