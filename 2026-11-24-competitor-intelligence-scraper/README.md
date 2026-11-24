# Competitor Intelligence Scraper

A tiny, CPU‑only Python CLI that crawls a competitor’s public website, extracts SEO‑relevant meta data and surfaces keyword trends. Perfect as a low‑cost micro‑SaaS ($5‑20 /mo) that can be embedded in larger lead‑gen or market‑visibility pipelines.

---

## 🎯 Aim
- **Strategic Sharpness** – give founders a data‑driven view of a rival’s messaging.
- **Automation** – run nightly on Railway/Vercel or a local Windows box.
- **Modular** – core functions (`crawl_site`, `extract_meta`, `summarize_keywords`) are import‑able for larger systems.

---

## ✨ Features
- Bread‑first crawl limited by depth (default 2) to keep runtime < 30 s on a modest CPU.
- Extracts title, description, and keywords from every page.
- Optional keyword frequency summary.
- Polite request throttling.
- Outputs a clean JSON report ready for dashboards or further analysis.

---

## 🛠️ Installation
```bash
pip install -r requirements.txt   # requests, beautifulsoup4
```

---

## 🚀 Usage
```bash
python main.py https://competitor.com -d 2 -k -o report.json
```
- `-d/--depth` – how many link hops to follow.
- `-k/--keywords` – add aggregated keyword list.
- `-o/--output` – destination file (defaults to `competitor_report.json`).

---

## 📦 SaaS‑Ready
Deploy the script as a scheduled job (e.g., GitHub Actions, Railway) and expose a thin FastAPI wrapper that accepts a URL and returns the JSON payload. Charge per‑site monthly.

---

## 🧩 Extensibility
- Import `crawl_site` in a larger analytics pipeline.
- Swap the HTML parser for lxml for speed.
- Add sentiment analysis on descriptions using a free local model.

---

## 🏷️ Tags
#AIMastery #Strategy #Finance

---

## License
MIT – free for commercial use.
