import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

def load_data(file_path: str) -> List[Dict[str, str]]:
    """Load CSV or JSON data file.
    Expected columns/keys: product, price, demand (optional).
    """
    p = Path(file_path)
    if not p.exists():
        sys.exit(f"[Error] File not found: {file_path}")
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text())
    if p.suffix.lower() == ".csv":
        lines = p.read_text().splitlines()
        header = [h.strip() for h in lines[0].split(",")]
        data = []
        for line in lines[1:]:
            if not line.strip():
                continue
            values = [v.strip() for v in line.split(",")]
            data.append(dict(zip(header, values)))
        return data
    sys.exit("[Error] Unsupported file type. Use .json or .csv")

def elasticity_estimate(price: float, demand: float) -> float:
    """Very simple linear elasticity estimator.
    Assumes demand changes 1% for each 1% price change.
    Returns elasticity coefficient (negative for normal goods).
    """
    # Placeholder: real world would need historic data.
    # Use demand as a proxy: higher demand => more elastic.
    return - (demand / max(price, 1e-3))

def suggest_price(cost: float, competitor_price: float, elasticity: float, margin_target: float = 0.2) -> Tuple[float, str]:
    """Calculate a price recommendation.
    - cost: internal cost of the product
    - competitor_price: average market price
    - elasticity: price elasticity coefficient (negative)
    - margin_target: desired gross margin (default 20%)
    Returns (price, rationale).
    """
    # Base price: cost plus target margin
    base_price = cost / (1 - margin_target)
    # Adjust towards competitor based on elasticity magnitude
    # More elastic (|e| large) => stay close to competitor
    # Less elastic => can deviate for higher margin
    weight = min(max(abs(elasticity) / 5, 0), 1)  # scale 0‑1
    suggested = weight * competitor_price + (1 - weight) * base_price
    # Ensure price covers cost
    if suggested < cost * 1.01:
        suggested = cost * 1.01
    rationale = (
        f"base_price={base_price:.2f}, competitor={competitor_price:.2f}, "
        f"elasticity={elasticity:.2f}, weight={weight:.2f}"
    )
    return round(suggested, 2), rationale

def process_items(data: List[Dict[str, str]], cost_field: str, demand_field: str) -> List[Dict[str, str]]:
    results = []
    for item in data:
        try:
            product = item.get("product") or item.get("name") or "unknown"
            price = float(item["price"])
            cost = float(item[cost_field])
            demand = float(item.get(demand_field, 1))  # fallback demand=1
        except (KeyError, ValueError) as e:
            print(f"[Warning] Skipping row due to missing/invalid data: {e}", file=sys.stderr)
            continue
        elasticity = elasticity_estimate(price, demand)
        suggested, rationale = suggest_price(cost, price, elasticity)
        results.append({
            "product": product,
            "current_price": price,
            "cost": cost,
            "suggested_price": suggested,
            "rationale": rationale,
        })
    return results

def output_results(results: List[Dict[str, str]], fmt: str, out_path: str = None):
    if fmt == "json":
        out = json.dumps(results, indent=2)
    else:  # markdown table
        header = "| Product | Current | Cost | Suggested | Rationale |\n|---|---|---|---|---|"
        rows = []
        for r in results:
            rows.append(
                f"| {r['product']} | {r['current_price']} | {r['cost']} | {r['suggested_price']} | {r['rationale']} |"
            )
        out = "\n".join([header] + rows)
    if out_path:
        Path(out_path).write_text(out)
        print(f"[Info] Results written to {out_path}")
    else:
        print(out)

def main():
    parser = argparse.ArgumentParser(
        description="Pricing Leverage Simulator – a lightweight CLI to suggest competitive prices based on cost, market price and simple elasticity estimation."
    )
    parser.add_argument("data", help="Path to input CSV or JSON containing product, price, and cost fields.")
    parser.add_argument("--cost-field", default="cost", help="Column/key name for internal cost (default: cost).")
    parser.add_argument("--demand-field", default="demand", help="Column/key name for demand proxy (default: demand).")
    parser.add_argument("--output", "-o", help="File to write results (defaults to stdout).")
    parser.add_argument("--format", "-f", choices=["json", "md"], default="md", help="Output format.")
    args = parser.parse_args()

    data = load_data(args.data)
    results = process_items(data, args.cost_field, args.demand_field)
    if not results:
        sys.exit("[Error] No valid rows processed.")
    output_results(results, args.format, args.output)

if __name__ == "__main__":
    main()
