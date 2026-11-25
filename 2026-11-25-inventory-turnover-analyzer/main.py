import csv
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime

def parse_inventory(file_path):
    """Parse inventory CSV.
    Expected columns: sku, product_name, stock_quantity, cost_price
    """
    inventory = {}
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sku = row['sku'].strip()
                inventory[sku] = {
                    'name': row.get('product_name', '').strip(),
                    'stock': int(row.get('stock_quantity', 0)),
                    'cost': float(row.get('cost_price', 0.0)),
                }
            except Exception as e:
                print(f"Skipping inventory row due to error: {e}", file=sys.stderr)
    return inventory

def parse_sales(file_path, start_date=None, end_date=None):
    """Parse sales CSV.
    Expected columns: date, sku, units_sold, revenue
    Dates in ISO format (YYYY-MM-DD).
    Returns mapping sku -> total units sold in period.
    """
    sales = defaultdict(int)
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sale_date = datetime.strptime(row['date'].strip(), '%Y-%m-%d').date()
                if start_date and sale_date < start_date:
                    continue
                if end_date and sale_date > end_date:
                    continue
                sku = row['sku'].strip()
                units = int(row.get('units_sold', 0))
                sales[sku] += units
            except Exception as e:
                print(f"Skipping sales row due to error: {e}", file=sys.stderr)
    return sales

def compute_turnover(inventory, sales, period_days):
    """Calculate inventory turnover ratio per SKU.
    Turnover = Cost of Goods Sold / Average Inventory
    For simplicity, COGS = units_sold * cost_price.
    Average inventory approximated as (opening stock + closing stock) / 2.
    Closing stock = opening stock - units_sold (non‑negative).
    """
    results = []
    for sku, data in inventory.items():
        opening_stock = data['stock']
        units_sold = sales.get(sku, 0)
        closing_stock = max(opening_stock - units_sold, 0)
        avg_inventory = (opening_stock + closing_stock) / 2
        if avg_inventory == 0:
            turnover = None
        else:
            cogs = units_sold * data['cost']
            turnover = cogs / avg_inventory
        results.append({
            'sku': sku,
            'name': data['name'],
            'opening_stock': opening_stock,
            'units_sold': units_sold,
            'closing_stock': closing_stock,
            'average_inventory': round(avg_inventory, 2),
            'turnover_ratio': round(turnover, 2) if turnover is not None else None,
            'turnover_days': round(period_days / turnover, 1) if turnover and turnover > 0 else None,
        })
    return sorted(results, key=lambda x: (x['turnover_ratio'] is None, x['turnover_ratio']))

def output_results(results, output_path=None, json_output=False):
    headers = ['SKU', 'Name', 'Opening', 'Sold', 'Closing', 'AvgInv', 'Turnover', 'DaysToTurn']
    lines = ["\t".join(headers)]
    for r in results:
        line = [
            r['sku'],
            r['name'],
            str(r['opening_stock']),
            str(r['units_sold']),
            str(r['closing_stock']),
            f"{r['average_inventory']:.2f}",
            f"{r['turnover_ratio']:.2f}" if r['turnover_ratio'] is not None else 'N/A',
            f"{r['turnover_days']:.1f}" if r['turnover_days'] is not None else 'N/A',
        ]
        lines.append("\t".join(line))
    output = "\n".join(lines)
    if json_output:
        json_data = json.dumps(results, indent=2, default=str)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
        else:
            print(json_data)
    else:
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)

def parse_date(s):
    return datetime.strptime(s, '%Y-%m-%d').date()

def main():
    parser = argparse.ArgumentParser(
        description='Inventory Turnover Analyzer – compute turnover ratios for Teddy3 products')
    parser.add_argument('--inventory', required=True, help='Path to inventory CSV')
    parser.add_argument('--sales', required=True, help='Path to sales CSV')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD) for sales period')
    parser.add_argument('--end', help='End date (YYYY-MM-DD) for sales period')
    parser.add_argument('--output', help='File to write tab‑separated results (default: stdout)')
    parser.add_argument('--json', action='store_true', help='Emit JSON instead of TSV')
    args = parser.parse_args()

    start_date = parse_date(args.start) if args.start else None
    end_date = parse_date(args.end) if args.end else None
    if not end_date:
        end_date = datetime.today().date()
    if not start_date:
        # default to last 30 days
        start_date = end_date.replace(day=1)
    period_days = (end_date - start_date).days or 1

    inventory = parse_inventory(args.inventory)
    sales = parse_sales(args.sales, start_date, end_date)
    results = compute_turnover(inventory, sales, period_days)
    output_results(results, args.output, args.json)

if __name__ == '__main__':
    main()
