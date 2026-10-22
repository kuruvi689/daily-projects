import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime

def load_competitor_data(path):
    """Load competitor data from CSV.
    Expected columns: initiative,category,impact,likelihood,owner,notes
    """
    data = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean and type‑cast fields
            row['impact'] = float(row.get('impact', 0) or 0)
            row['likelihood'] = float(row.get('likelihood', 0) or 0)
            data.append(row)
    return data

def score_initiative(item):
    """Simple risk‑reward score: impact * likelihood.
    Higher means more strategic importance.
    """
    return item['impact'] * item['likelihood']

def group_by_category(items):
    groups = defaultdict(list)
    for it in items:
        groups[it['category']].append(it)
    return groups

def generate_swot(groups):
    """Create a minimal SWOT‑style matrix.
    - Strengths: high score, owned by us (owner == 'self')
    - Weaknesses: low score, owned by us
    - Opportunities: high score, owned by competitor
    - Threats: low score, owned by competitor
    """
    swot = {'Strengths': [], 'Weaknesses': [], 'Opportunities': [], 'Threats': []}
    for cat, items in groups.items():
        for it in items:
            sc = score_initiative(it)
            if it['owner'].lower() == 'self':
                target = 'Strengths' if sc >= 5 else 'Weaknesses'
            else:
                target = 'Opportunities' if sc >= 5 else 'Threats'
            swot[target].append({
                'initiative': it['initiative'],
                'category': cat,
                'score': round(sc, 2),
                'notes': it['notes']
            })
    return swot

def output_json(swot, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(swot, f, indent=2, ensure_ascii=False)

def output_markdown(swot, out_path):
    lines = [f"# Strategic Initiative Map – {datetime.now().strftime('%Y-%m-%d')}", ""]
    for quadrant in ['Strengths', 'Weaknesses', 'Opportunities', 'Threats']:
        lines.append(f"## {quadrant}")
        items = swot[quadrant]
        if not items:
            lines.append("_None_\n")
            continue
        for it in items:
            lines.append(f"- **{it['initiative']}** (Category: {it['category']}, Score: {it['score']})")
            if it['notes']:
                lines.append(f"  - Notes: {it['notes']}")
        lines.append("")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    parser = argparse.ArgumentParser(
        description='Map competitor and internal initiatives into a simple SWOT matrix.'
    )
    parser.add_argument('csv_file', help='Path to input CSV file with initiatives')
    parser.add_argument('--json', default='swot.json', help='Path for JSON output')
    parser.add_argument('--md', default='swot.md', help='Path for Markdown report')
    args = parser.parse_args()

    try:
        data = load_competitor_data(args.csv_file)
    except Exception as e:
        sys.exit(f'Error loading CSV: {e}')

    groups = group_by_category(data)
    swot = generate_swot(groups)
    output_json(swot, args.json)
    output_markdown(swot, args.md)
    print(f'SWOT matrix written to {args.json} and {args.md}')

if __name__ == '__main__':
    main()
