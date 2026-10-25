# Strategic Leverage Matrix

A tiny, CPU‑only Python CLI that turns public news into a **strategic leverage matrix** for any competitor or brand.

## 🎯 Aim
- **Real problem**: Early‑stage founders need quick intel on how rivals are positioning (pricing, partnerships, regulatory moves) without expensive services.
- **SaaS‑ready**: Package as a micro‑service (`$5‑20/mo`) that runs nightly, stores JSON reports, and surfaces a simple dashboard.
- **Modular**: Core functions (`fetch_rss`, `parse_bing_news`, `analyse`) are pure Python and can be imported into larger automation pipelines (e.g., n8n, Railway).

## ✨ Features
- Pulls the last N days of news from **Bing News RSS** (free, no API key).
- Scores headlines against a user‑provided keyword list (pricing, partnership, acquisition, …).
- Generates a concise JSON report with total relevance score, per‑keyword hit counts, and top‑10 items.
- Tiny on‑disk cache to respect rate limits.

## 🛠️ Tech Stack
- Python 3.9+ (standard library)
- `requests` – HTTP client
- `beautifulsoup4` – XML parsing

## 📦 Installation
```bash
pip install requests beautifulsoup4
```

## 🚀 Quick Start
```bash
python main.py "Teddy3" -k price partnership launch
```
Creates `leverage_report.json`:
```json
{
  "company": "Teddy3",
  "generated_at": "2026-10-25T12:34:56Z",
  "lookback_days": 7,
  "keywords": ["price", "partnership", "launch"],
  "total_relevance_score": 42,
  "keyword_hits": {"price": 3, "partnership": 1, "launch": 2},
  "top_items": [
    {"title": "Teddy3 launches AI‑driven pricing engine", "link": "...", "pubDate": "2026-10-24T08:00:00", "score": 5},
    ...
  ]
}
```

## ⚙️ Arguments
| Flag | Description |
|------|-------------|
| `company` | Target brand/competitor |
| `-k/--keywords` | Space‑separated list of focus terms (default: generic strategic terms) |
| `-d/--days` | Look‑back window (default 7) |
| `-o/--output` | Path for the JSON report (default `leverage_report.json`) |

## 📈 SaaS Model
1. **Scheduler** – Run the CLI nightly via a lightweight Windows service or Railway cron.
2. **Multi‑tenant storage** – Prefix reports by client ID.
3. **Dashboard** – Simple static site reads the JSON and visualises scores.
4. **Pricing** – Tiered by number of monitored companies (1‑5 for $5, 6‑20 for $12, unlimited for $20).

## 🏷️ Tags
#AIMastery #Strategy #Finance

---
*Built for Sivanesh’s multi‑venture workflow – lightweight, open, and ready to monetize.*
