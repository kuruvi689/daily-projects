# Prompt Optimizer CLI

**Category:** #AIMastery #Strategy #Finance

A tiny, CPU‑only Python CLI that inspects your LLM prompts, counts tokens, and flags common pitfalls. Perfect as a micro‑SaaS ($5‑20 /mo) that helps developers ship cheaper, higher‑quality AI features.

---

## Features
- **Token budgeting** using `tiktoken` (compatible with OpenAI, Groq, Claude models).
- Detects missing **System** instructions, unreplaced `{{placeholders}}`, overly long contexts, and excessive blank lines.
- Generates a clean **Markdown report** with actionable suggestions.
- Stand‑alone `main.py` (< 250 lines) and pure‑Python core that can be imported by larger services.

---

## Installation
```bash
pip install -r requirements.txt  # only tiktoken needed
```

---

## Usage
```bash
python main.py prompts.txt            # creates prompt_report.md
python main.py prompts.txt -o out.md   # custom output path
```

**prompts.txt** format – one or many prompts separated by a line containing exactly `---`. Each prompt may include optional sections:
```
System: You are a helpful financial advisor.
User: Summarize the latest market news.
Assistant: ...
---
User: What's the best way to save for retirement?
```

---

## Output Example
```markdown
# Prompt Optimization Report

## Prompt 1
**System** (12 tokens):
```
You are a helpful financial advisor.
```
**User** (8 tokens):
```
Summarize the latest market news.
```
**Overall:** ✅ Good to go

---

## Prompt 2
**User** (9 tokens):
```
What's the best way to save for retirement?
```
**Overall:** ⚠️ Issues detected
**Suggestions:**
- Missing System instruction – add a clear role for the model.
- Prompt uses 150 tokens; consider trimming to ≤800 for cost efficiency.
```

---

## Extending / Integrating
The core functions (`load_prompts`, `parse_sections`, `evaluate_prompt`) live in `main.py` and can be imported:
```python
from main import evaluate_prompt, parse_sections
```
Use them in a FastAPI endpoint, a scheduled job, or embed in a larger SaaS platform.

---

## License
MIT – free for commercial use.
