# Decision Path Mapper

**Category:** #AIMastery #Strategy #Finance

## Overview
`decision-path-mapper` is a lightweight Python CLI that turns raw decision‑outcome logs into strategic insights. By computing expected utilities and surfacing best‑practice suggestions, it helps founders, product teams, and finance professionals iterate faster on high‑impact choices.

## Key Features
- **CSV‑based ingestion** – simple export from any spreadsheet or CRM.
- **Expected utility calculation** – multiplies probability × utility for each option.
- **Best‑option recommendation** – flags decisions that consistently favor the optimal choice.
- **JSON report** – ready to feed into dashboards, newsletters, or SaaS billing.
- **Zero‑dependency** – pure standard‑library, runs on any Windows CPU‑only machine.

## Installation
```bash
pip install decision-path-mapper
```
*(The package contains only the `main.py` file; no external libraries are required.)*

## Usage
```bash
python -m decision_path_mapper decisions.csv -o report.json
```
- `decisions.csv` – your decision log (see **CSV Format** below).
- `report.json` – generated report with summaries, expected utilities, and next‑step suggestions.

### CSV Format
| date | decision | option | probability | outcome | utility |
|------|----------|--------|-------------|---------|---------|
| 2024-10-01 | pricing_strategy | premium | 0.4 | higher margin | 12000 |
| 2024-10-01 | pricing_strategy | discount | 0.6 | increased volume | 8000 |

- **date** – `YYYY-MM-DD`
- **decision** – identifier for the decision point (e.g., `pricing_strategy`).
- **option** – label of the option taken.
- **probability** – estimated chance this option leads to the outcome (0‑1).
- **outcome** – free‑form description.
- **utility** – numeric value representing value (revenue, score, etc.).

## Output Example
```json
{
  "generated_at": "2026-11-21T12:34:56Z",
  "summary": { ... },
  "expected_utilities": {
    "pricing_strategy": {
      "options": [
        {"option": "premium", "expected_utility": 4800},
        {"option": "discount", "expected_utility": 4800}
      ],
      "best_option": "premium",
      "best_expected_utility": 4800
    }
  },
  "suggestions": {
    "pricing_strategy": "Review needed – best option 'premium' used only 0%"
  }
}
```

## SaaS Potential
- **Micro‑service API** – expose the JSON report via a cheap Flask endpoint (`$5‑$20/mo`).
- **Multi‑tenant dashboards** – integrate with existing analytics stacks.
- **Add‑ons** – automated probability calibration, Slack notifications, or Excel export.

## Extensibility
The core functions (`load_decisions`, `compute_expected_utilities`, `suggest_next`) are pure Python and can be imported into larger workflows, n8n automations, or internal libraries.

## License
MIT – free for commercial and personal use.
