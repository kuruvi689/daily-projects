# Decision Matrix CLI

A lightweight, CPU‑only Python CLI that helps founders, product managers, and finance enthusiasts make **transparent, data‑driven decisions**.

## ✨ What it solves
- **Strategic overload** – Quickly compare multiple options against any set of criteria (cost, impact, risk, time, etc.).
- **Documentation gap** – Every matrix is persisted and can be exported to Markdown for stakeholder reviews.
- **SaaS‑ready micro‑service** – The core logic (`add`, `show`, `ranking`) is isolated in a tiny JSON store, making it easy to wrap with a Flask/FastAPI wrapper and charge $5‑20 / month for a hosted decision‑engine.

## 🚀 Features
- Add a decision matrix with custom criteria and scores.
- List all saved matrices.
- Show a detailed view with automatic ranking (simple sum weighting).
- Export any matrix to a clean Markdown report.
- Delete obsolete entries.
- Zero‑dependency – only Python standard library, perfect for Windows laptops without a GPU.

## 📦 Installation
```bash
pip install decision-matrix-cli  # (or copy the repo and run `python -m pip install .`)
```

## 🛠️ Usage
```bash
# Add a new decision
decision-matrix add "Launch new hoodie line" \
  --criteria Cost,Impact,Time \
  --options "In‑house" "Outsource" \
  --scores "7,8,5" "5,9,6"

# List all decisions
decision-matrix list

# Show a matrix (replace <id> with the printed ID)
decision-matrix show <id>

# Export to markdown
decision-matrix export <id> --output ./hoodie_decision.md

# Delete an entry
decision-matrix delete <id>
```

## 📂 Project Structure
- `main.py` – Single‑file CLI (≤250 lines).
- `~/.decision_matrix/matrix.json` – Local JSON store, automatically created.

## 💡 Extending
The JSON format is deliberately simple, so you can:
- Add weighted criteria (multiply scores before summing).
- Plug into a web service (FastAPI endpoint that reads/writes the same JSON).
- Integrate with Google Sheets via the API for team collaboration.

## 🏷️ Tags
#AIMastery #Strategy #Finance

---
*Built for Sivanesh’s multi‑venture ecosystem – from streetwear to fintech and AI agents.*
