# Strategic Initiative Mapper

A lightweight Python CLI that turns raw initiative data (yours and competitors) into a **SWOT‑style matrix** you can share with investors, teammates, or embed in larger SaaS products.

---

## 🎯 Aim
Help founders and strategists quickly surface **high‑leverage moves** and hidden threats without leaving the terminal. Perfect for:
- Early‑stage streetwear brands evaluating market moves
- Finance lead‑gen teams comparing loan product roll‑outs
- Any B2B SaaS founder needing a one‑page strategic snapshot

---

## 🚀 Features
- **CSV input** – simple spreadsheet export (initiative, category, impact, likelihood, owner, notes)
- **Risk‑reward scoring** (`impact × likelihood`)
- Automatic grouping by category
- Generates both **JSON** (machine‑readable) and **Markdown** (human‑readable) reports
- No external dependencies – runs on pure Python stdlib, ideal for CPU‑only Windows machines

---

## 🛠️ Installation
```bash
pip install strategic-initiative-mapper
```
*(the package is a single‑file CLI, no heavy dependencies)*

---

## 📋 Usage
```bash
python -m strategic_initiative_mapper initiatives.csv \
    --json output.json \
    --md report.md
```
- `initiatives.csv` – your data file (see **Sample CSV** below)
- `--json` – path for machine‑readable output (default `swot.json`)
- `--md`  – path for a ready‑to‑share markdown report (default `swot.md`)

### Sample CSV
| initiative | category | impact | likelihood | owner | notes |
|------------|----------|--------|------------|-------|-------|
| New hoodie line | Product | 8 | 0.7 | self | Limited‑edition drop |
| AI‑driven loan scoring | Finance | 9 | 0.9 | competitor | Patented algorithm |
| Instagram live sales | Marketing | 5 | 0.6 | self | Seasonal promo |
| Referral program | Growth | 4 | 0.4 | competitor | Low conversion |

---

## 📦 SaaS‑Ready
- **Micro‑service endpoint** – wrap the CLI in a FastAPI route that calls the same functions.
- **Pricing** – $5‑20 / month per seat for unlimited SWOT generations.
- **Modular core** – `load_competitor_data`, `score_initiative`, `generate_swot` are import‑able for larger pipelines.

---

## 🏷️ Tags
#AIMastery #Strategy #Finance

---

## License
MIT – free for commercial use.
