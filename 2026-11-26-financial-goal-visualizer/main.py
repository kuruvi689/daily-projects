import json, os, sys, argparse, datetime, textwrap, pathlib

def load_goals(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_goals(path, goals):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(goals, f, indent=2)

def add_goal(args):
    goals = load_goals(args.file)
    goal = {
        "id": len(goals) + 1,
        "name": args.name,
        "target_amount": float(args.target),
        "current_amount": 0.0,
        "deadline": args.deadline,
        "created": datetime.date.today().isoformat()
    }
    goals.append(goal)
    save_goals(args.file, goals)
    print(f"Added goal #{goal['id']}: {goal['name']}")

def record_progress(args):
    goals = load_goals(args.file)
    for g in goals:
        if g['id'] == args.id:
            g['current_amount'] = float(args.amount)
            save_goals(args.file, goals)
            print(f"Updated goal #{g['id']} current amount to {g['current_amount']}")
            return
    print(f"Goal id {args.id} not found.")

def list_goals(args):
    goals = load_goals(args.file)
    if not goals:
        print("No goals found.")
        return
    for g in goals:
        pct = (g['current_amount'] / g['target_amount'] * 100) if g['target_amount'] else 0
        deadline = g['deadline'] or "—"
        print(textwrap.dedent(f"""
        [{g['id']}] {g['name']}
            Target: ${g['target_amount']:.2f}
            Current: ${g['current_amount']:.2f} ({pct:.1f}%)
            Deadline: {deadline}
        """).strip())

def summary(args):
    goals = load_goals(args.file)
    if not goals:
        print("No goals to summarize.")
        return
    total_target = sum(g['target_amount'] for g in goals)
    total_current = sum(g['current_amount'] for g in goals)
    overall_pct = (total_current / total_target * 100) if total_target else 0
    print("=== Financial Goal Summary ===")
    print(f"Total Target: ${total_target:.2f}")
    print(f"Total Saved : ${total_current:.2f} ({overall_pct:.1f}%)")
    upcoming = sorted([g for g in goals if g['deadline']], key=lambda x: x['deadline'])[:5]
    if upcoming:
        print("\nUpcoming deadlines:")
        for g in upcoming:
            days = (datetime.datetime.strptime(g['deadline'], "%Y-%m-%d").date() - datetime.date.today()).days
            print(f"  - {g['name']} in {days} day(s)")

def init_parser():
    parser = argparse.ArgumentParser(prog='financial-goal-visualizer', description='Track and visualize personal financial goals.')
    parser.add_argument('--file', default=str(pathlib.Path.home() / '.fgv_goals.json'), help='JSON file to store goals')
    sub = parser.add_subparsers(dest='cmd')
    add = sub.add_parser('add', help='Add a new financial goal')
    add.add_argument('name', help='Goal name')
    add.add_argument('target', help='Target amount (e.g., 5000)')
    add.add_argument('--deadline', help='Deadline YYYY-MM-DD', default='')
    add.set_defaults(func=add_goal)
    rec = sub.add_parser('record', help='Record current saved amount for a goal')
    rec.add_argument('id', type=int, help='Goal ID')
    rec.add_argument('amount', help='Current saved amount')
    rec.set_defaults(func=record_progress)
    lst = sub.add_parser('list', help='List all goals')
    lst.set_defaults(func=list_goals)
    sumr = sub.add_parser('summary', help='Show aggregate summary')
    sumr.set_defaults(func=summary)
    return parser

def main():
    parser = init_parser()
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == '__main__':
    main()
