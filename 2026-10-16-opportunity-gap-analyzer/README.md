# Opportunity Gap Analyzer

A lightweight Python CLI that compares a plain‑text resume against a collection of job description texts, surfacing **skill gaps** and providing a concise markdown report.

## 🎯 Aim
- **Strategic Sharpness** – Identify high‑leverage up‑skill opportunities.
- **Micro‑SaaS ready** – Turn the CLI into a $5‑20 /month service that ingests resumes and job feeds via an API.
- **Modular core** – `load_resume`, `load_job_descriptions`, `compute_gap` are reusable functions for larger talent‑intelligence platforms.

## ✨ Features
- Pure‑Python, std‑lib only (no GPU, no heavy dependencies).
- Works on any Windows CPU‑only machine.
- Generates a markdown report with per‑job missing skills and an aggregated frequency list.

## 🛠️ Installation
```bash
pip install -r requirements.txt   # currently empty – stdlib only
```

## 🚀 Usage
```bash
python main.py path/to/resume.txt path/to/jobs_dir -o my_report.md
```
- `resume.txt` – plain‑text resume.
- `jobs_dir` – folder of `*.txt` job description files.
- `-o` – optional output file (defaults to `gap_report.md`).

## 📦 SaaS Path
1. Wrap the core functions in a FastAPI endpoint.
2. Store resumes/jobs in S3 or a simple DB.
3. Charge per analysis or per month for unlimited scans.

## 🏷️ Tags
#AIMastery #Strategy #Finance

## License
MIT – free for commercial and personal use.
