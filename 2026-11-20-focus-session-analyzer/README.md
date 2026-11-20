# Focus Session Analyzer

A tiny, SaaS‑ready CLI that turns raw focus‑session logs into actionable insight.

## What it does
- **Ingests** a CSV exported from any timer (start, end, project, interruptions).
- **Aggregates** total time, session count and interruption count **overall** and **per project**.
- **Outputs** a human‑readable markdown summary to the console.
- **Optionally** writes a detailed JSON payload for downstream dashboards or automation.

## Why it matters
- **#AIMastery** – Leverages simple time‑series analysis to surface productivity patterns.
- **#Strategy** – Helps freelancers and small teams allocate effort where it yields the most ROI.
- **#Finance** – By quantifying focused work you can tie billable hours to revenue forecasts.

## Installation
```bash
pip install focus-session-analyzer   # (or copy the repo and run directly)
```
*No external services are required; the tool runs on any CPU‑only Windows machine.*

## Usage
```bash
python -m focus_session_analyzer path/to/log.csv        # markdown report
python -m focus_session_analyzer path/to/log.csv -j out.json  # also write JSON
```
The CSV must contain the columns **start**, **end**, **project**, **interruptions**. Times can be ISO strings (`2026-11-20 14:30:00`) or simple `HH:MM`.

## Example CSV
```
start,end,project,interruptions
2026-11-19 09:00:00,2026-11-19 10:15:00,backend,2
2026-11-19 10:30:00,2026-11-19 11:00:00,frontend,0
2026-11-19 13:00:00,2026-11-19 14:45:00,backend,1
```

## Extending the tool
- Import `load_sessions`, `aggregate` or `report` in larger Python services.
- Swap the CSV reader for a database query to analyse real‑time data.
- Hook the JSON output into a weekly email or a low‑code dashboard (e.g., n8n, Railway).

## License
MIT – free for commercial use.
