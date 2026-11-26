# Financial Goal Visualizer

A lightweight, CPU‑only Python CLI to help individuals **track, visualize, and stay accountable** to personal financial goals.

## Features
- **Add** new goals with target amount and optional deadline.
- **Record** progress anytime; stores data locally in a JSON file (`~/.fgv_goals.json`).
- **List** all goals with percentage completion.
- **Summary** view showing total targets, overall saved amount, and upcoming deadlines.
- No external dependencies – runs with the Python standard library only.
- Ideal as a micro‑SaaS ($5‑20/mo) offering API‑wrapped endpoints for dashboards or mobile apps.

## Installation
```bash
pip install financial-goal-visualizer   # package name placeholder
```
Or clone the repo and run directly:
```bash
python main.py --help
```

## Usage
```bash
# Add a goal
python main.py add "Emergency Fund" 5000 --deadline 2024-12-31

# Record progress (goal id shown via `list`)
python main.py record 1 1500

# List all goals
python main.py list

# Show summary
python main.py summary
```

## Extensibility
- Core functions (`load_goals`, `save_goals`, calculations) are pure Python and can be imported into larger services or a FastAPI wrapper.
- JSON storage can be swapped for a cloud DB with minimal changes.

## Tags
#AIMastery #Strategy #Finance
