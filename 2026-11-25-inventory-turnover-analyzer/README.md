# Inventory Turnover Analyzer

A lightweight **Python CLI** that helps street‑wear founders (like Teddy3) understand how efficiently their stock turns into revenue.

## 🎯 Aim
- **Financial Independence**: Spot dead‑stock early, free up cash, and improve profit margins.
- **Micro‑SaaS Ready**: Turn the CLI into a hosted service ($5‑20 / month) that accepts CSV uploads and returns turnover reports.
- **Modular**: Core functions (`parse_inventory`, `parse_sales`, `compute_turnover`) are pure Python and can be imported into larger dashboards or n8n workflows.

## 🛠️ Stack
- **Language**: Python 3.10+
- **Runtime**: CPU‑only, Windows friendly
- **Dependencies**: Standard library only (no external packages)

## 📦 Installation
```bash
pip install inventory-turnover-analyzer   # (if published) or clone this repo
```

## 🚀 Usage
```bash
python main.py \
  --inventory inventory.csv \
  --sales sales.csv \
  [--start 2024-10-01] [--end 2024-10-31] \
  [--output report.tsv] [--json]
```
- `inventory.csv` – columns: `sku,product_name,stock_quantity,cost_price`
- `sales.csv` – columns: `date,sku,units_sold,revenue`
- `--json` – emit JSON instead of tab‑separated values.

## 📈 What the report shows
| Column | Meaning |
|---|---|
| **SKU / Name** | Identifier and product name |
| **Opening** | Stock at period start |
| **Sold** | Units sold in the period |
| **Closing** | Remaining stock |
| **AvgInv** | Average inventory (approx.) |
| **Turnover** | Cost‑of‑Goods‑Sold ÷ AvgInv |
| **DaysToTurn** | Approx. days to sell current inventory |

## 💡 SaaS Hook
Expose the same logic via a tiny FastAPI endpoint that accepts multipart CSVs and returns JSON. Charge a flat monthly fee; the compute cost stays negligible on a modest VM.

## 🏷️ Tags
#AIMastery #Strategy #Finance

## 📜 License
MIT – feel free to adapt for your own brand.
