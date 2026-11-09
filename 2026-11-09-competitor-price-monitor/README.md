# Competitor Price Monitor

A lightweight, CPU‑only Python CLI that lets founders and analysts **track competitor product prices** in real time.

## 🎯 Aim
- Provide a **micro‑service** that can be packaged as a $5‑20/month SaaS offering.
- Enable **strategic sharpness** by surfacing price changes before they impact your own pricing.
- Keep the core logic **modular** so it can be embedded in larger automation pipelines (n8n, Railway, etc.).

## ✨ Features
- **Config‑driven** – supply a JSON file with URLs and CSS selectors for the price element.
- **Free & open** – uses only `requests` and `beautifulsoup4`; no paid APIs.
- **CLI‑first** – run once or as a continuous poller (`--interval` seconds).
- **JSON report** – easy to consume by dashboards, webhook integrations, or downstream analytics.
- **Windows‑friendly** – works on a vanilla Windows machine without GPU.

## 🚀 Quick Start
```bash
# Install dependencies
pip install requests beautifulsoup4

# Create a config (prices.json)
cat > prices.json <<EOF
[
  {"url": "https://example.com/shirt", "selector": ".price"},
  {"url": "https://shop.com/hoodie", "selector": "#price-tag"}
]
EOF

# Run the monitor once
python main.py -c prices.json

# Run every 6 hours (21600 seconds)
python main.py -c prices.json -i 21600
```

## 📦 Integration
- **n8n**: Use the `Execute Command` node to invoke the CLI and parse the JSON output.
- **Railway / Vercel**: Deploy as a scheduled job that writes the report to a bucket or database.
- **Micro‑service**: Wrap the `monitor` function in a FastAPI endpoint for on‑demand price checks.

## 🛠️ Architecture
```
config.json → monitor() → fetch_page() → extract_price() → report.json
```
All heavy lifting is pure Python; the only external libraries are tiny HTTP/HTML parsers.

## 📜 License
MIT – feel free to adapt, extend, and sell as part of your own SaaS.

#Strategy #Finance #AIMastery
