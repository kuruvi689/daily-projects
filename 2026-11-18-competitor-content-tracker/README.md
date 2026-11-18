# Competitor Content Tracker

A tiny, CPU‑only Python CLI that watches competitor websites for content changes.

## 🎯 Aim
- **Strategic Sharpness**: Detect when a rival updates product pages, pricing tables, or marketing copy.
- **Micro‑SaaS ready**: Offer a subscription‑based monitoring service ($5‑20 /mo) per set of URLs.
- **Modular core**: `fetch_html`, `extract_text`, and `hash_content` are pure functions that can be reused in larger pipelines (e.g., n8n workflows).
- **Zero‑cost tech stack**: Uses only the Python standard library; optional `requests` and `beautifulsoup4` improve reliability but are not required.

## 📦 Installation
```bash
pip install competitor-content-tracker
# optional for better HTML parsing
pip install requests beautifulsoup4
```

## 🚀 Usage
```bash
python -m competitor_content_tracker https://example.com https://rival.co
```
Outputs a short status list:
```
[NEW] https://example.com
[UPDATED] https://rival.co
[OK] https://stable.com
```

### JSON mode (for API integration)
```bash
python -m competitor_content_tracker https://example.com --json
```
```json
[
  {"url": "https://example.com", "status": "new"},
  {"url": "https://rival.co", "status": "changed"}
]
```

## 🗂 Data Persistence
Records are stored under `~/.competitor_tracker/records.json`. The file holds the SHA‑256 hash of the last‑seen content and the UTC timestamp of the check.

## 🛠 Extending
- Plug the core functions into an n8n workflow to trigger Slack/Email alerts.
- Deploy on Railway or Vercel as a scheduled job (cron) and expose a tiny HTTP endpoint.
- Combine with a pricing‑leverage simulator for deeper competitive analysis.

## 📜 License
MIT – feel free to adapt and sell as a SaaS offering.

#AIMastery #Strategy #Finance
