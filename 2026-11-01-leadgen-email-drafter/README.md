# leadgen-email-drafter

**Category:** #Finance #AIMastery #Strategy

A lightweight Python CLI that turns a CSV of loan‑lead contacts into
personalised outreach emails using a Jinja2 template.  The output is a set of
plain‑text files ready to be fed into any mailing system (SendGrid, Mailchimp,
SMTP, etc.).

---

## Why this tool?
- **Revenue‑ready:** Wrap the CLI in a tiny FastAPI endpoint and sell it as a
  micro‑service ($5‑20 / month) to fintech founders who need fast, compliant
  outreach.
- **Modular:** Core functions (`load_leads`, `render_email`, `write_email`) are
  pure Python and can be imported into larger pipelines (n8n, Railway, etc.).
- **Zero‑GPU, low‑cost:** Only the `jinja2` package is required; everything else
  lives in the standard library.
- **Windows‑friendly:** Tested on Windows 10/11 with a CPU‑only machine.

---

## Quick Start
```bash
# Install the single dependency
pip install jinja2

# Prepare a CSV (must contain at least `name` and `email` columns)
cat > leads.csv <<EOF
name,email,company,loan_amount
Alice,alice@example.com,Acme Corp,50000
Bob,bob@example.com,Delta Ltd,75000
EOF

# Create a template (Jinja2 syntax)
cat > template.txt <<EOF
Hi {{ name }},

I noticed {{ company }} is looking for a {{ loan_amount }} ₹ loan. Our
unsecured business‑loan product at Suryoday Bank can fund you in 48 hours.

Let me know a good time to discuss.

Best,
Sivanesh
EOF

# Run the generator
python main.py leads.csv template.txt output_emails/
```

The `output_emails/` folder will contain `alice_alice@example.com.txt` and
`bob_bob@example.com.txt` with the rendered content.

---

## Integration Ideas
- **n8n:** Use the CLI as a subprocess node after a lead‑capture webhook.
- **Railway / Vercel:** Deploy as a serverless function that accepts CSV and
  template payloads, returns a zip of generated emails.
- **CRM Sync:** Hook the output into HubSpot or Zoho via their APIs.

---

## License
MIT – free for commercial use.
