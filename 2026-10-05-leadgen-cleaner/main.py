import argparse, csv, re, sys, json, os
from collections import Counter

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows, reader.fieldnames

def save_csv(path, rows, fieldnames):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def is_valid_email(email):
    if not email:
        return False
    # simple RFC‑5322 lightweight check
    pattern = r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
    return re.fullmatch(pattern, email) is not None

def is_valid_phone(phone):
    if not phone:
        return False
    # Indian mobile numbers: 10 digits, optional +91 or 0 prefix
    cleaned = re.sub(r"[^0-9]", "", phone)
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if cleaned.startswith('0') and len(cleaned) == 11:
        cleaned = cleaned[1:]
    return len(cleaned) == 10 and cleaned.isdigit()

def is_valid_gstin(gstin):
    if not gstin:
        return False
    # 15‑char alphanumeric, first 2 digits state code
    return bool(re.fullmatch(r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{3}", gstin.upper()))

def clean_rows(rows, email_col, phone_col, gstin_col):
    cleaned = []
    stats = Counter()
    for r in rows:
        email = r.get(email_col, '').strip()
        phone = r.get(phone_col, '').strip()
        gstin = r.get(gstin_col, '').strip()
        email_ok = is_valid_email(email)
        phone_ok = is_valid_phone(phone)
        gstin_ok = is_valid_gstin(gstin)
        if email_ok and phone_ok and gstin_ok:
            cleaned.append(r)
        else:
            stats['rejected'] += 1
            if not email_ok:
                stats['bad_email'] += 1
            if not phone_ok:
                stats['bad_phone'] += 1
            if not gstin_ok:
                stats['bad_gstin'] += 1
    stats['accepted'] = len(cleaned)
    return cleaned, stats

def print_summary(stats, total):
    summary = {
        'total_rows': total,
        'accepted': stats.get('accepted', 0),
        'rejected': stats.get('rejected', 0),
        'bad_email': stats.get('bad_email', 0),
        'bad_phone': stats.get('bad_phone', 0),
        'bad_gstin': stats.get('bad_gstin', 0),
    }
    print(json.dumps(summary, indent=2))

def parse_args():
    p = argparse.ArgumentParser(description='LeadGen Cleaner – validate & prune CSV lead lists for Suryoday Bank')
    p.add_argument('input', help='Path to input CSV')
    p.add_argument('output', help='Path to cleaned CSV')
    p.add_argument('--email-col', default='email', help='Column name for email')
    p.add_argument('--phone-col', default='phone', help='Column name for phone')
    p.add_argument('--gstin-col', default='gstin', help='Column name for GSTIN')
    return p.parse_args()

def main():
    args = parse_args()
    if not os.path.isfile(args.input):
        sys.exit(f'Input file not found: {args.input}')
    rows, fieldnames = load_csv(args.input)
    cleaned, stats = clean_rows(rows, args.email_col, args.phone_col, args.gstin_col)
    save_csv(args.output, cleaned, fieldnames)
    print_summary(stats, len(rows))

if __name__ == '__main__':
    main()
