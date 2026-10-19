# Market Visibility Analyzer

A lightweight, CPU‑only Python CLI that scrapes a list of competitor or market URLs, extracts the page *title* and *meta description*, and outputs a structured report. Perfect as a low‑cost SaaS micro‑service for founders, marketers, or analysts who need quick visibility snapshots without building a full‑blown crawler.

---

## 🎯 Aim
- **Strategic Sharpness** – surface invisible leverage by understanding how competitors position themselves in search results.
- **Micro‑service ready** – can be containerised and sold for $5‑20 / month as a "visibility‑audit" endpoint.
- **Modular core** – `fetch_url`, `parse_meta`, and `analyze_urls` are pure functions reusable in larger pipelines (lead‑gen, competitor‑intel, etc.).

---

## ✨ Features
- Accepts a plain‑text or JSON file of URLs.
- Retrieves HTML with a safe timeout and custom User‑Agent.
- Parses title & meta description using **BeautifulSoup**.
- Emits JSON or CSV reports.
- Zero GPU, pure CPU, works on Windows.

---

## 📦 Installation
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage
```bash
python main.py competitors.txt -o report.csv -f csv
```
- `competitors.txt` – one URL per line (or a JSON array).
- `-o` – destination file (default `visibility-report.json`).
- `-f` – `json` (default) or `csv`.

---

## 🛠️ Extending
- Swap `fetch_url` for an async HTTP client for higher throughput.
- Add OpenAI/Gemini summarisation of descriptions for richer insights.
- Integrate with n8n or Railway as a scheduled job.

---

## 🏷️ Tags
#AIMastery #Strategy #Finance
