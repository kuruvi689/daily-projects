import csv
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

def load_decisions(file_path: Path):
    """Load decisions from a CSV file.
    Expected columns: date,decision,option,probability,outcome,utility
    - date: YYYY-MM-DD
    - decision: identifier for the decision point
    - option: the chosen option label
    - probability: estimated probability (0-1) of this option leading to the outcome
    - outcome: description of the result
    - utility: numeric utility (can be profit, score, etc.)
    """
    decisions = []
    with file_path.open(newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['date'] = datetime.strptime(row['date'], "%Y-%m-%d").date()
                row['probability'] = float(row['probability'])
                row['utility'] = float(row['utility'])
                decisions.append(row)
            except Exception as e:
                print(f"Skipping malformed row {row}: {e}", file=sys.stderr)
    return decisions

def summarize(decisions):
    """Create a high‑level summary per decision point."""
    summary = {}
    for d in decisions:
        key = d['decision']
        if key not in summary:
            summary[key] = {'options': []}
        summary[key]['options'].append({
            'option': d['option'],
            'probability': d['probability'],
            'utility': d['utility'],
            'outcome': d['outcome'],
            'date': d['date'].isoformat()
        })
    return summary

def compute_expected_utilities(summary):
    """For each decision, compute expected utility per option and overall best option."""
    results = {}
    for decision, data in summary.items():
        exp_utils = []
        for opt in data['options']:
            exp = opt['probability'] * opt['utility']
            exp_utils.append({
                'option': opt['option'],
                'expected_utility': round(exp, 2),
                'probability': opt['probability'],
                'utility': opt['utility'],
                'outcome': opt['outcome']
            })
        best = max(exp_utils, key=lambda x: x['expected_utility'])
        results[decision] = {
            'options': exp_utils,
            'best_option': best['option'],
            'best_expected_utility': best['expected_utility']
        }
    return results

def suggest_next(decision_results, history):
    """Suggest next decision based on past success rate.
    If a decision's best option has been chosen >60% of the time, suggest it;
    otherwise flag for review.
    """
    suggestions = {}
    for decision, res in decision_results.items():
        chosen_counts = Counter([opt['option'] for opt in history[decision]['options']])
        total = sum(chosen_counts.values())
        best_opt = res['best_option']
        best_ratio = chosen_counts.get(best_opt, 0) / total if total else 0
        if best_ratio >= 0.6:
            suggestions[decision] = f"Continue with '{best_opt}' (used {best_ratio:.0%} of the time)."
        else:
            suggestions[decision] = f"Review needed – best option '{best_opt}' used only {best_ratio:.0%}.")
    return suggestions

def main():
    parser = argparse.ArgumentParser(description='Decision Path Mapper – turn decision logs into actionable insights.')
    parser.add_argument('csv_file', type=Path, help='Path to decisions CSV')
    parser.add_argument('-o', '--output', type=Path, default=Path('decision_report.json'), help='JSON report destination')
    args = parser.parse_args()

    if not args.csv_file.is_file():
        print(f"File not found: {args.csv_file}", file=sys.stderr)
        sys.exit(1)

    decisions = load_decisions(args.csv_file)
    if not decisions:
        print("No valid decisions loaded.", file=sys.stderr)
        sys.exit(1)

    summary = summarize(decisions)
    exp_results = compute_expected_utilities(summary)
    suggestions = suggest_next(exp_results, summary)

    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'summary': summary,
        'expected_utilities': exp_results,
        'suggestions': suggestions
    }

    args.output.write_text(json.dumps(report, indent=2, default=str))
    print(f"Report written to {args.output}")

if __name__ == '__main__':
    main()
