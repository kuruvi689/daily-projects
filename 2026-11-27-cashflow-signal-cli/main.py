import argparse, csv, json, sys, math, statistics, os

def load_transactions(path):
    transactions = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Expect columns: date, amount, description
            try:
                amount = float(row.get('amount', 0))
            except ValueError:
                continue
            transactions.append({
                'date': row.get('date', ''),
                'amount': amount,
                'desc': row.get('description', row.get('desc', '')).lower()
            })
    return transactions

def categorize(tx, rules):
    for cat, keywords in rules.items():
        if any(k in tx['desc'] for k in keywords):
            return cat
    return 'uncategorized'

def group_by_month(transactions):
    groups = {}
    for tx in transactions:
        month = tx['date'][:7]  # YYYY-MM
        groups.setdefault(month, []).append(tx)
    return groups

def detect_spikes(month_tx, window=3, z_thresh=2.0):
    # compute total per category per month
    cat_month_totals = {}
    for month, txs in month_tx.items():
        for tx in txs:
            cat = tx['category']
            cat_month_totals.setdefault(cat, {}).setdefault(month, 0)
            cat_month_totals[cat][month] += tx['amount']
    # for each category compute rolling mean/std and flag outliers
    alerts = []
    for cat, month_vals in cat_month_totals.items():
        sorted_months = sorted(month_vals)
        amounts = [month_vals[m] for m in sorted_months]
        for i in range(len(amounts)):
            start = max(0, i - window)
            window_vals = amounts[start:i]
            if len(window_vals) < 2:
                continue
            mean = statistics.mean(window_vals)
            stdev = statistics.stdev(window_vals)
            if stdev == 0:
                continue
            z = (amounts[i] - mean) / stdev
            if abs(z) >= z_thresh:
                alerts.append({
                    'category': cat,
                    'month': sorted_months[i],
                    'amount': amounts[i],
                    'z_score': round(z, 2)
                })
    return alerts

def summarize(month_tx):
    summary = {}
    for month, txs in month_tx.items():
        total = sum(tx['amount'] for tx in txs)
        by_cat = {}
        for tx in txs:
            cat = tx['category']
            by_cat.setdefault(cat, 0)
            by_cat[cat] += tx['amount']
        summary[month] = {'total': round(total, 2), 'by_category': {c: round(v,2) for c,v in by_cat.items()}}
    return summary

def main():
    parser = argparse.ArgumentParser(description='Cashflow Signal CLI – detect spending spikes and monthly summaries')
    parser.add_argument('csv_file', help='Path to transactions CSV (date,amount,description)')
    parser.add_argument('--output', '-o', default='summary.json', help='File to write JSON summary')
    args = parser.parse_args()

    if not os.path.isfile(args.csv_file):
        sys.exit(f'File not found: {args.csv_file}')

    # Simple keyword‑based categories – extendable
    category_rules = {
        'food': ['restaurant', 'cafe', 'food', 'coffee', 'dine'],
        'transport': ['uber', 'taxi', 'bus', 'metro', 'fuel', 'gas'],
        'entertainment': ['movie', 'netflix', 'concert', 'game'],
        'shopping': ['amazon', 'store', 'mall', 'clothing', 'apparel'],
        'salary': ['salary', 'payroll', 'remuneration'],
        'rent': ['rent', 'lease', 'apartment'],
        'utilities': ['electric', 'water', 'internet', 'phone']
    }

    txs = load_transactions(args.csv_file)
    for tx in txs:
        tx['category'] = categorize(tx, category_rules)

    month_groups = group_by_month(txs)
    summary = summarize(month_groups)
    alerts = detect_spikes(month_groups)

    result = {'monthly_summary': summary, 'spike_alerts': alerts}
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f'Summary written to {args.output}')
    if alerts:
        print('\n⚠️  Spike alerts detected:')
        for a in alerts:
            print(f"- {a['month']} | {a['category']}: {a['amount']} (z={a['z_score']})")
    else:
        print('No significant spikes found.')

if __name__ == '__main__':
    main()
