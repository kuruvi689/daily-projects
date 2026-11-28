# Lead‑Gen Email Personalizer

A tiny, SaaS‑ready Python CLI that turns raw loan‑lead data into **personalised follow‑up emails** ready to be fed into any mailing platform.

---

## 🎯 Aim
- **Problem**: Manual copy‑pasting and editing of email drafts for each loan lead wastes time and introduces errors.
- **Solution**: Provide a single command that consumes a JSONL lead feed and a simple `{{placeholder}}` template, then spits out ready‑to‑send email files.
- **Business angle**: Offer this as a micro‑service ($5‑20/mo) where users upload their lead CSV/JSONL and receive a zip of ready emails, or integrate via an API.

---

## 🚀 Features
- **Zero‑dependency core** – runs on the Python standard library (optional Jinja2 for power users).
- **Template‑driven** – use a built‑in default or drop a custom `.txt` into `templates/`.
- **Batch processing** – handles thousands of leads in seconds.
- **File‑safe output** – each email saved as `NN_email@example.com.txt`.
- **Modular design** – core functions (`load_template`, `render_template`, `parse_leads`) are importable for larger systems.

---

## 🛠️ Installation
```bash
# Clone the repo
git clone https://github.com/yourname/lead-gen-email-personalizer.git
cd lead-gen-email-personalizer

# (Optional) create a venv
python -m venv .venv && .venv\Scripts\activate

# Install requirements (empty for stdlib only)
pip install -r requirements.txt
```

---

## 📖 Usage
```bash
python main.py leads.jsonl --template my_template.txt --out-dir emails
```
- `leads.jsonl` – one JSON object per line. Example line:
```json
{"first_name": "Ravi", "email": "ravi@example.com", "loan_type": "business", "max_amount": "500000", "agent_name": "Anita"}
```
- `--template` – name of a file placed in `templates/`. If omitted, the built‑in template is used.
- `--out-dir` – where rendered `.txt` files are saved.

---

## 📦 SaaS Packaging Idea
1. Wrap the CLI in a tiny FastAPI endpoint that accepts a file upload and returns a zip of generated emails.
2. Charge a monthly subscription based on monthly email volume (e.g., up to 5k emails = $5, 20k = $15).
3. Deploy on Railway or Railway‑free tier; the tool stays CPU‑only and inexpensive.

---

## 🏷️ Tags
#AIMastery #Strategy #Finance

---

## License
MIT – free for personal and commercial use.
