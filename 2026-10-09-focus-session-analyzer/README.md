# Focus Session Analyzer

A tiny, SaaS‑ready CLI that turns raw focus‑session logs into actionable insights.

## ✨ What it does
- **Consumes** a CSV export from any timer app (e.g., Toggl, Clockify) with columns `start,end,project,interruptions`.
- **Computes** total time, average session length, interruptions and per‑project breakdowns.
- **Outputs** a clean Markdown report ready for newsletters, dashboards, or automated emails.

## 🎯 Why it matters
- **Productivity owners** (like Sivanesh) can charge a modest subscription ($5‑$20/mo) for a hosted version that ingests daily logs and emails a weekly summary.
- **Modular core** (`load_sessions`, `summarize`) can be imported into larger SaaS back‑ends, RAG pipelines, or internal dashboards.
- **Zero‑cost** – pure Python standard library, runs on any Windows CPU‑only machine.

## 🛠️ Installation
```bash
pip install focus-session-analyzer
```
*(the package name mirrors the repo slug; the only dependency is the standard library.)*

## 🚀 Usage
```bash
python -m focus_session_analyzer path/to/log.csv [-o summary.md]
```
- **`log.csv`** – your raw session export.
- **`-o`** – optional output file; otherwise the markdown is printed to stdout.

### Sample CSV
```csv
start,end,project,interruptions
2026-10-01 09:00:00,2026-10-01 10:15:00,frontend,1
2026-10-01 11:00:00,2026-10-01 12:30:00,backend,0
```

## 📦 Output (Markdown)
```markdown
# Focus Session Analysis

## Overall Summary
- Total Sessions: 2
- Total Time: 165.0 minutes
- Avg Session Length: 82.5 minutes
- Total Interruptions: 1

## By Project
### frontend
- Sessions: 1
- Total Time: 75.0 minutes
- Avg Session: 75.0 minutes
- Interruptions: 1

### backend
- Sessions: 1
- Total Time: 90.0 minutes
- Avg Session: 90.0 minutes
- Interruptions: 0
```

## 📡 SaaS‑ready roadmap
1. **Webhook endpoint** – POST CSV, get markdown back.
2. **User auth & storage** – associate logs with accounts.
3. **Scheduled email** – weekly PDF/HTML summary.
4. **Dashboard UI** – visual charts using Plotly (optional premium add‑on).

---

#AIMastery #Strategy #Finance
