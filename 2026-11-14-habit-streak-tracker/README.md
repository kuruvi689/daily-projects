# Habit Streak Tracker

A tiny, CPU‑only Python CLI to record daily habit completions, compute current/longest streaks and give quick completion‑rate reports.

## Features
- **Add** a habit entry for today (or any ISO date).
- **Status** shows total days logged, current streak, and longest streak.
- **Report** prints a one‑liner for every habit with a rolling completion rate (default 30 days).
- Stores data locally in `~/.habit_streaks.json` – no external services, fully SaaS‑ready as a micro‑service.
- Pure standard‑library implementation (no dependencies).

## Installation
```bash
pip install habit-streak-tracker  # if packaged, otherwise copy main.py
```

## Usage
```bash
# Mark a habit as done for today
habit-streak-tracker add reading

# Mark with a specific date
habit-streak-tracker add meditation --date 2026-11-01

# View streak information
habit-streak-tracker status reading

# Get a quick overview of all habits (last 30 days)
habit-streak-tracker report

# Custom window for report
habit-streak-tracker report --days 7
```

## Data Model
The JSON file is a simple dictionary:
```json
{
  "reading": ["2026-11-01", "2026-11-02"],
  "meditation": ["2026-11-01"]
}
```
Each array holds ISO‑formatted dates when the habit was marked.

## Extensibility
- Import `load_data` / `save_data` in other Python services.
- Replace the storage backend (e.g., Redis, Firestore) without touching core logic.
- Hook into CI pipelines to generate daily habit badges.

## License
MIT – free for personal and commercial use.

#AIMastery #Strategy #Finance
