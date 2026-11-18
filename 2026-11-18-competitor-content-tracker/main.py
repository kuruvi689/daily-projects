import json
import hashlib
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Optional imports – if unavailable, fallback to stdlib urllib
try:
    import requests
except ImportError:
    requests = None
    import urllib.request as urllib_request
    import urllib.error as urllib_error

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

DATA_DIR = Path.home() / ".competitor_tracker"
DATA_FILE = DATA_DIR / "records.json"

def load_records() -> Dict[str, Dict]:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_records(records: Dict[str, Dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def fetch_html(url: str) -> str:
    if requests:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    else:
        try:
            with urllib_request.urlopen(url, timeout=10) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except urllib_error.URLError as e:
            raise RuntimeError(f"Failed to fetch {url}: {e}")

def extract_text(html: str) -> str:
    if BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        # Remove scripts/styles and get visible text
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split())
    else:
        # Very naive fallback – strip tags manually
        import re
        clean = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)
        clean = re.sub(r"<style.*?</style>", "", clean, flags=re.DOTALL)
        clean = re.sub(r"<!--.*?-->", "", clean, flags=re.DOTALL)
        clean = re.sub(r"<[^>]+>", " ", clean)
        return " ".join(clean.split())

def hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def check_urls(urls: List[str]) -> List[Tuple[str, str, bool]]:
    """Return list of (url, change_type, changed_flag).
    change_type: 'new' | 'changed' | 'unchanged'
    """
    records = load_records()
    results = []
    for url in urls:
        try:
            html = fetch_html(url)
            text = extract_text(html)
            cur_hash = hash_content(text)
        except Exception as e:
            print(f"[WARN] {url}: {e}", file=sys.stderr)
            continue
        prev = records.get(url)
        if not prev:
            change = "new"
            changed = True
        elif prev["hash"] != cur_hash:
            change = "changed"
            changed = True
        else:
            change = "unchanged"
            changed = False
        results.append((url, change, changed))
        # Update record
        records[url] = {"hash": cur_hash, "last_checked": datetime.utcnow().isoformat()}
    save_records(records)
    return results

def format_output(results: List[Tuple[str, str, bool]]) -> str:
    lines = []
    for url, change, changed in results:
        if change == "new":
            lines.append(f"[NEW] {url}")
        elif change == "changed":
            lines.append(f"[UPDATED] {url}")
        else:
            lines.append(f"[OK] {url}")
    return "\n".join(lines)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Track competitor website content changes – lightweight CLI"
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more competitor URLs to monitor",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of plain text",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    results = check_urls(args.urls)
    if args.json:
        out = [
            {"url": url, "status": status}
            for url, status, _ in results
        ]
        print(json.dumps(out, indent=2))
    else:
        print(format_output(results))

if __name__ == "__main__":
    main()
