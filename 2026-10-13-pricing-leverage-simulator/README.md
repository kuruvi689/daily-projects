# Pricing Leverage Simulator

**Category**: Strategic Sharpness – *Game‑theory / competitor intelligence*  
**Tags**: #AIMastery #Strategy #Finance

A tiny, SaaS‑ready Python CLI that helps a streetwear brand (or any small business) set prices that balance cost, desired margin and competitor pressure. It works entirely offline, uses only the standard library and fits on a CPU‑only Windows laptop.

---

## Features
- **Input flexibility** – CSV or JSON with `product`, `price` (market), `cost` and optional `demand` fields.
- **Simple elasticity model** – estimates price elasticity from current price & demand proxy.
- **Margin‑driven suggestion** – starts from a target gross margin (default 20 %).
- **Competitive weighting** – more elastic products stay close to market price; less elastic can command higher margins.
- **Modular core** – `load_data`, `elasticity_estimate`, `suggest_price` are pure functions you can import into larger systems.
- **Output** – Markdown table (ideal for quick copy‑paste into a pitch deck) or JSON for API consumption.

---

## Installation
```bash
pip install pricing-leverage-simulator   # package name is just the repo slug
```
*(No external dependencies – pure stdlib.)*

---

## Quick Start
```bash
# data.csv example
product,price,cost,demand
Teddy‑Hoodie,2500,1500,120
Cap,800,400,300

# Run the CLI
python -m pricing_leverage_simulator data.csv --format md
```
Output:
```markdown
| Product | Current | Cost | Suggested | Rationale |
|---|---|---|---|---|
| Teddy‑Hoodie | 2500.0 | 1500.0 | 2100.0 | base_price=1875.00, competitor=2500.00, elasticity=-0.48, weight=0.10 |
| Cap | 800.0 | 400.0 | 560.0 | base_price=500.00, competitor=800.00, elasticity=-0.38, weight=0.08 |
```

---

## Usage Details
| Option | Description |
|---|---|
| `data` | Path to CSV/JSON file containing product info |
| `--cost-field` | Column name for internal cost (default `cost`) |
| `--demand-field` | Column name for demand proxy (default `demand`). Higher numbers mean more price‑sensitive |
| `-o / --output` | Write result to a file instead of stdout |
| `-f / --format` | `md` (default) or `json` |

---

## Extending the Core
```python
from pricing_leverage_simulator import suggest_price, elasticity_estimate

# plug your own elasticity model or margin policy
new_price, reason = suggest_price(cost=1200, competitor_price=2600, elasticity=-1.2, margin_target=0.25)
```
Integrate this logic into a SaaS dashboard, n8n workflow, or automated pricing micro‑service.

---

## License
MIT – free for commercial use.

---

## Why This Is High‑Leverage
- **Revenue impact** – a 5 % price tweak on a $10k monthly volume yields $500 extra profit.
- **Scalable** – the same engine can power a multi‑tenant SaaS offering at $5‑20 / month per brand.
- **Low friction** – runs anywhere Python runs, no GPU, no external API keys.

Ready to price smarter? Clone, install, and start feeding your sales data.
