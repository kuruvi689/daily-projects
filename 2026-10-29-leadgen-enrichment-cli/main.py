import sys, json, argparse, csv, os, datetime, hashlib, urllib.parse, urllib.request

def load_leads(path):
    leads = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads

def save_leads(leads, path):
    if not leads:
        return
    fieldnames = leads[0].keys()
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

def hash_email(email):
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()[:10]

def enrich_lead(lead):
    # basic enrichment – deterministic pseudo‑score and geo‑lookup
    # 1) pseudo credit score (300‑850) derived from email hash & revenue
    email = lead.get('email', '')
    rev = lead.get('annual_revenue', '0').replace(',', '')
    try:
        rev_val = float(rev)
    except ValueError:
        rev_val = 0.0
    base = int(hash_email(email), 16) % 551 + 300  # 300‑850 range
    # bump score for higher revenue (simple linear scaling)
    score = min(850, base + int(rev_val / 100000))
    lead['pseudo_credit_score'] = str(score)
    # 2) simple geo enrichment via OpenStreetMap Nominatim (free, no key)
    address = lead.get('address', '')
    if address:
        query = urllib.parse.urlencode({'format': 'json', 'limit': 1, 'q': address})
        url = f'https://nominatim.openstreetmap.org/search?{query}'
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data:
                    lead['lat'] = data[0].get('lat', '')
                    lead['lon'] = data[0].get('lon', '')
        except Exception:
            pass
    # 3) timestamp of enrichment
    lead['enriched_at'] = datetime.datetime.utcnow().isoformat() + 'Z'
    return lead

def batch_enrich(leads, dry_run=False):
    enriched = []
    for lead in leads:
        if dry_run:
            enriched.append({**lead, 'pseudo_credit_score': 'N/A', 'lat': 'N/A', 'lon': 'N/A'})
        else:
            enriched.append(enrich_lead(lead))
    return enriched

def parse_args():
    p = argparse.ArgumentParser(description='LeadGen Enrichment CLI – add pseudo credit score and geo data')
    p.add_argument('input', help='Path to input CSV of leads')
    p.add_argument('output', help='Path to write enriched CSV')
    p.add_argument('--dry-run', action='store_true', help='Show columns that would be added without API calls')
    return p.parse_args()

def main():
    args = parse_args()
    if not os.path.isfile(args.input):
        sys.stderr.write(f'Input file not found: {args.input}\n')
        sys.exit(1)
    leads = load_leads(args.input)
    enriched = batch_enrich(leads, dry_run=args.dry_run)
    save_leads(enriched, args.output)
    print(f'Enriched {len(enriched)} leads → {args.output}')

if __name__ == '__main__':
    main()
