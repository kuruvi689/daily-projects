# Meeting Notes Action Extractor

A tiny, CPU‑only Python CLI that turns raw meeting transcripts into a clean markdown task list.

## 🎯 Goal
- **Real problem**: Teams lose track of decisions and owners after meetings.
- **SaaS‑ready**: Offer as a $5‑20 / month micro‑service that ingests notes and returns actionable items.
- **Modular**: Core parsing logic (`parse_actions`) can be imported by larger workflow engines (e.g., n8n, Airflow).
- **Zero‑cost**: Uses only the Python standard library – no external APIs or GPU.

## 🛠️ Features
- Detects lines like `- Follow up with vendor Owner: @alice Due: 2024-12-01`.
- Generates a markdown file with a numbered list, owners, and due dates.
- Optional JSON dump for downstream automation.
- Works on Windows, Linux, macOS – CPU only.

## 📦 Installation
```bash
pip install meeting-notes-action-extractor  # package name placeholder
```
*(The package contains only this `main.py` – no heavy dependencies.)*

## 🚀 Usage
```bash
python -m meeting_notes_action_extractor notes.txt -o actions.md --json
```
- `notes.txt` – your raw meeting notes (plain text or markdown).
- `-o actions.md` – writes the markdown task list.
- `--json` – prints a JSON array of extracted items to stdout.

### Example Input
```
- Review Q3 budget Owner: @bob Due: 2024-10-15
- Update onboarding flow Owner: @carol Due: 2024-09-30
```
### Example Output (Markdown)
```markdown
# Action Items

1. **Review Q3 budget**  
   - Owner: @bob  
   - Due: 2024-10-15

2. **Update onboarding flow**  
   - Owner: @carol  
   - Due: 2024-09-30
```

## 📈 SaaS Model
1. **Self‑hosted** – customers run the CLI in a CI/CD pipeline.
2. **Hosted API** – expose the `parse_actions` function behind a lightweight Flask/FastAPI wrapper (adds < 5 ms latency on a single‑core VM).
3. **Billing** – per‑month quota of processed notes (e.g., 10 k notes for $9/mo).

## 🧩 Extensibility
- Import `parse_actions` in other Python projects.
- Swap the regex with a more sophisticated NLP model later without touching the CLI.
- Hook into n8n via the `--json` flag.

## 🏷️ Tags
#AIMastery #Strategy #Finance

---
*Built for Sivanesh’s multi‑project ecosystem – lightweight, reusable, and ready for productisation.*
