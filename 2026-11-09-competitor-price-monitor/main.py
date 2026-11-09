import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Optional dependencies
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.stderr.write("Missing required packages. Install with: pip install requests beautifulsoup4\n")
    sys.exit(1)

DEFAULT_OUTPUT = Path("price_report.json")

def fetch_page(url: str, timeout: int = 10) -> str:
    """Return the raw HTML of *url* or raise an exception on failure."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; competitor-price-monitor/1.0)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def extract_price(html: str, selector: str) -> str:
    """Extract price text using a CSS *selector*.
    Returns the stripped text or raises ValueError if not found.
    """
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one(selector)
    if not el:
        raise ValueError(f"Price element not found for selector '{selector}'")
    return el.get_text(strip=True)

def monitor(urls: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Process a list of URL/selector dicts and return price data.
    Each dict must contain:
        - "url": product page URL
        - "selector": CSS selector that isolates the price element
    """
    results = []
    for entry in urls:
        url = entry.get("url")
        selector = entry.get("selector")
        if not url or not selector:
            continue
        try:
            html = fetch_page(url)
            price = extract_price(html, selector)
            status = "ok"
        except Exception as e:
            price = None
            status = f"error: {e}"
        results.append({
            "url": url,
            "selector": selector,
            "price": price,
            "status": status,
            "timestamp": int(time.time())
        })
    return results

def load_config(path: Path) -> List[Dict[str, str]]:
    """Load JSON config file containing a list of url/selector objects.
    Example:
    [
        {"url": "https://example.com/item1", "selector": ".price"},
        {"url": "https://example.com/item2", "selector": "#price"}
    ]
    """
    if not path.is_file():
        sys.stderr.write(f"Config file not found: {path}\n")
        sys.exit(1)
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, list):
            raise ValueError("Config JSON must be a list")
        return data
    except Exception as e:
        sys.stderr.write(f"Failed to parse config: {e}\n")
        sys.exit(1)

def save_report(report: List[Dict[str, Any]], out_path: Path) -> None:
    out_path.write_text(json.dumps(report, indent=2))
    print(f"Report written to {out_path}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Competitor Price Monitor – CLI to fetch and compare product prices from competitor sites."
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        required=True,
        help="Path to JSON config file with url/selector entries."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="File to write JSON price report (default: price_report.json)."
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=0,
        help="If >0, run continuously every N seconds (useful for SaaS polling)."
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    while True:
        report = monitor(config)
        save_report(report, args.output)
        if args.interval <= 0:
            break
        print(f"Waiting {args.interval}s before next run…")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
