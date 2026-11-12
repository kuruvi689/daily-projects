import json
import argparse
import random
import sys
from pathlib import Path
from typing import List, Dict, Any

def load_scenarios(file_path: Path) -> List[Dict[str, Any]]:
    """Load a JSON file describing possible actions and their effects.

    The file must contain a list of scenario objects:
    {
        "name": "Launch new product",
        "probability": 0.3,               # chance this action is taken
        "outcomes": [
            {"impact": {"revenue": 50000, "brand": 10}, "prob": 0.6},
            {"impact": {"revenue": -20000, "brand": -5}, "prob": 0.4}
        ]
    }
    """
    try:
        with file_path.open() as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Root element must be a list of scenarios")
        return data
    except Exception as e:
        sys.exit(f"❌ Failed to load scenarios: {e}")

def validate_scenarios(scenarios: List[Dict[str, Any]]) -> None:
    for i, s in enumerate(scenarios):
        if "name" not in s or "probability" not in s or "outcomes" not in s:
            raise ValueError(f"Scenario {i} missing required keys")
        if not 0 <= s["probability"] <= 1:
            raise ValueError(f"Scenario {i} has invalid probability")
        total = sum(o.get("prob", 0) for o in s["outcomes"])
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Outcomes of scenario {i} must sum to 1 (got {total})")

def simulate_once(scenarios: List[Dict[str, Any]]) -> Dict[str, float]:
    result: Dict[str, float] = {}
    for s in scenarios:
        if random.random() <= s["probability"]:
            # pick an outcome based on its internal distribution
            r = random.random()
            cumulative = 0.0
            for o in s["outcomes"]:
                cumulative += o["prob"]
                if r <= cumulative:
                    for k, v in o["impact"].items():
                        result[k] = result.get(k, 0.0) + v
                    break
    return result

def run_simulation(scenarios: List[Dict[str, Any]], iterations: int) -> List[Dict[str, float]]:
    aggregates: List[Dict[str, float]] = []
    for _ in range(iterations):
        aggregates.append(simulate_once(scenarios))
    return aggregates

def summarize(results: List[Dict[str, float]]) -> Dict[str, Any]:
    if not results:
        return {}
    summary: Dict[str, Any] = {}
    keys = set().union(*[r.keys() for r in results])
    for k in keys:
        values = [r.get(k, 0.0) for r in results]
        summary[k] = {
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p90": sorted(values)[int(0.9 * len(values))]
        }
    return summary

def export_json(data: Any, path: Path) -> None:
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    print(f"📁 Exported to {path}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monte‑Carlo scenario simulator for strategic decision making"
    )
    parser.add_argument("scenario_file", type=Path, help="JSON file with scenario definitions")
    parser.add_argument("-n", "--iterations", type=int, default=10000, help="Number of Monte Carlo runs")
    parser.add_argument("-o", "--output", type=Path, default=Path("simulation_result.json"), help="Where to write full run data")
    parser.add_argument("-s", "--summary", type=Path, default=Path("simulation_summary.json"), help="Where to write aggregated summary")
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenario_file)
    validate_scenarios(scenarios)
    print(f"🔧 Loaded {len(scenarios)} scenarios. Running {args.iterations} iterations …")

    results = run_simulation(scenarios, args.iterations)
    export_json(results, args.output)
    summary = summarize(results)
    export_json(summary, args.summary)
    print("✅ Simulation complete. Summary metrics:")
    for metric, vals in summary.items():
        print(f"  • {metric}: mean={vals['mean']:.2f}, p90={vals['p90']:.2f}, min={vals['min']:.2f}, max={vals['max']:.2f}")

if __name__ == "__main__":
    main()
