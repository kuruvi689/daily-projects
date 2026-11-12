# Scenario Simulator CLI

**Tag:** #AIMastery #Strategy #Finance

A tiny, SaaS‑ready command‑line tool that lets founders, product managers, and finance teams model *what‑if* strategic choices using Monte‑Carlo simulation.

---

## Why this matters
- **Strategic Sharpness** – Quantify the impact of competing actions (e.g., new product launch, pricing change, marketing spend) without building a full‑blown analytics stack.
- **Decision Leverage** – Spot high‑variance moves, understand upside/downside risk, and communicate clear numbers to investors or stakeholders.
- **Micro‑service ready** – Deploy the CLI as a lightweight HTTP wrapper (FastAPI, Flask) and charge $5‑20 / month per tenant.

---

## Features
- Pure‑Python, standard‑library only (runs on any Windows CPU box).
- JSON‑based scenario definition – easy to integrate with existing data pipelines.
- Fast Monte‑Carlo engine (default 10k iterations, configurable).
- Generates two artefacts:
  1. `simulation_result.json` – raw outcome of every run.
  2. `simulation_summary.json` – mean, min, max, 90‑percentile for each KPI (revenue, brand, cost, etc.).
- Modular core (`run_simulation`, `simulate_once`, `summarize`) can be imported into larger Python services.

---

## Installation
```bash
pip install scenario-simulator-cli   # package name placeholder
```
*(No external dependencies – the `requirements.txt` is empty.)*

---

## Quick start
1. Create a `scenarios.json` file:
```json
[
  {
    "name": "Launch new sneaker line",
    "probability": 0.4,
    "outcomes": [
      {"impact": {"revenue": 120000, "brand": 15}, "prob": 0.7},
      {"impact": {"revenue": -30000, "brand": -5}, "prob": 0.3}
    ]
  },
  {
    "name": "Run flash sale",
    "probability": 0.6,
    "outcomes": [
      {"impact": {"revenue": 40000, "brand": -2}, "prob": 0.5},
      {"impact": {"revenue": 0, "brand": 0}, "prob": 0.5}
    ]
  }
]
```
2. Run the simulator:
```bash
python -m scenario_simulator_cli scenarios.json -n 20000
```
3. Review `simulation_summary.json` for the risk profile.

---

## Integration example (Python)
```python
from scenario_simulator_cli import run_simulation, summarize

scenarios = [...]  # load or build dicts
raw = run_simulation(scenarios, 5000)
print(summarize(raw))
```

---

## License
MIT – free for personal and commercial use.

---

## Next steps for a SaaS product
- Wrap the CLI in a tiny FastAPI app exposing `/simulate`.
- Store tenant definitions in a PostgreSQL table.
- Add authentication & usage metering.
- Offer a dashboard that visualises the summary.

---

*Empower strategic decisions with data‑driven confidence – one command at a time.*
