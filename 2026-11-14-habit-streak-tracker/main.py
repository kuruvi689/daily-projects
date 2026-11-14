import argparse
import json
import os
import sys
from datetime import datetime, timedelta

DATA_FILE = os.path.expanduser('~/.habit_streaks.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=True)

def today_str():
    return datetime.utcnow().date().isoformat()

def add_habit(args):
    data = load_data()
    habit = args.habit.lower()
    date = args.date or today_str()
    if habit not in data:
        data[habit] = []
    if date in data[habit]:
        print(f"[✖] Habit '{habit}' already marked for {date}.")
        return
    data[habit].append(date)
    data[habit].sort()
    save_data(data)
    print(f"[✔] Recorded '{habit}' for {date}.")

def status_habit(args):
    data = load_data()
    habit = args.habit.lower()
    if habit not in data or not data[habit]:
        print(f"No records for habit '{habit}'.")
        return
    dates = [datetime.fromisoformat(d).date() for d in data[habit]]
    dates_set = set(dates)
    today = datetime.utcnow().date()
    # current streak
    streak = 0
    cur = today
    while cur in dates_set:
        streak += 1
        cur -= timedelta(days=1)
    # longest streak
    longest = 0
    current = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current += 1
        else:
            longest = max(longest, current)
            current = 1
    longest = max(longest, current)
    print(f"Habit: {habit}\nTotal days logged: {len(dates)}\nCurrent streak: {streak}\nLongest streak: {longest}")

def report(args):
    data = load_data()
    if not data:
        print('No habit data found.')
        return
    for habit, dates in sorted(data.items()):
        dates_obj = [datetime.fromisoformat(d).date() for d in dates]
        dates_obj.sort()
        total = len(dates_obj)
        # compute completion rate over the last N days (default 30)
        window = args.days or 30
        start = datetime.utcnow().date() - timedelta(days=window-1)
        completed = sum(1 for d in dates_obj if d >= start)
        rate = (completed / window) * 100
        print(f"- {habit}: {total} days logged, last {window}d completion {rate:.1f}%")

def init_parser():
    parser = argparse.ArgumentParser(prog='habit-streak-tracker', description='Track daily habit streaks via a tiny CLI.')
    sub = parser.add_subparsers(dest='cmd')
    # add
    p_add = sub.add_parser('add', help='Mark a habit as completed for today or a given date.')
    p_add.add_argument('habit', help='Name of the habit')
    p_add.add_argument('--date', help='ISO date (YYYY-MM-DD). Defaults to today UTC.')
    p_add.set_defaults(func=add_habit)
    # status
    p_status = sub.add_parser('status', help='Show current and longest streak for a habit.')
    p_status.add_argument('habit', help='Name of the habit')
    p_status.set_defaults(func=status_habit)
    # report
    p_report = sub.add_parser('report', help='Brief overview of all habits.')
    p_report.add_argument('--days', type=int, help='Window in days for completion rate (default 30).')
    p_report.set_defaults(func=report)
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
