# Loan Eligibility Simulator

A lightweight, CPU‑only Python CLI that evaluates personal or small‑business loan applications in real‑time.

## 🎯 Aim
**#AIMastery #Strategy #Finance** – Provide founders, loan officers, and fintech SaaS platforms a fast, privacy‑first eligibility check that can be wrapped into a micro‑service ($5‑20 /mo).

## ✨ Features
- Pure‑Python, no external services – runs on any Windows machine.
- Simple JSON input / output – easy to integrate with n8n, Railway, or Vercel serverless functions.
- Core evaluation logic (`evaluate`) is library‑ready for larger pipelines.
- Transparent rationale for every decision.

## 🚀 Quick Start
```bash
# Install (nothing beyond the stdlib)
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt   # (empty)

# Run with inline JSON
echo '{"monthly_income":5000,"existing_debt":500,"credit_score":720,"business_years":3,"requested_amount":30000,"requested_term_months":48}' |
python -m loan_eligibility_simulator
```

## 📄 Input Schema
```json
{
  "monthly_income": number,
  "existing_debt": number,
  "credit_score": int (300‑850),
  "business_years": int,
  "requested_amount": number,
  "requested_term_months": int
}
```
All fields are required.

## 📤 Output Example
```json
{
  "approved": true,
  "approved_amount": 30000,
  "max_term_months": 48,
  "rationale": "DTI=12.00%, credit_factor=1.03, business_factor=0.80. Approved 30000 for up to 48 months."
}
```

## 🛠️ Extending
- Import `evaluate` in other services (e.g., FastAPI endpoint).
- Swap the simple payment model with an amortization calculator.
- Add risk‑weighting tables or ML‑based scoring later.

## 📦 Packaging
```bash
python -m pip install build
python -m build   # creates a wheel for SaaS deployment
```
Deploy the wheel to Railway, Railway‑Docker, or a simple Windows scheduled task.

## 📜 License
MIT – free for commercial use.
