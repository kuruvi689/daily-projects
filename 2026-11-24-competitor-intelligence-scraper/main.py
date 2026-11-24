import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

# --------------------------- Helper Functions ---------------------------

def fetch_url(url: str, timeout: int = 10) -> str:
    """Retrieve raw HTML from a URL with basic error handling."""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"[!] Failed to fetch {url}: {e}", file=sys.stderr)
        return ""


def extract_links(html: str, base_url: str) -> List[str]:
    """Return a list of absolute URLs found in the page's anchor tags."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            links.append(href)
        elif href.startswith("/"):
            links.append(base_url.rstrip('/') + href)
    return links


def extract_meta(html: str) -> Dict[str, str]:
    """Grab common SEO meta information useful for competitor intel."""
    soup = BeautifulSoup(html, "html.parser")
    meta = {}
    # Title
    if soup.title and soup.title.string:
        meta["title"] = soup.title.string.strip()
    # Description
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        meta["description"] = desc["content"].strip()
    # Keywords (if any)
    kw = soup.find("meta", attrs={"name": "keywords"})
    if kw and kw.get("content"):
        meta["keywords"] = kw["content"].strip()
    return meta


def crawl_site(start_url: str, depth: int = 2, delay: float = 1.0) -> List[Dict[str, Any]]:
    """Bread‑first crawl limited to *depth* levels.
    Returns a list of page dictionaries containing URL and extracted meta.
    """
    visited = set()
    frontier = [(start_url, 0)]
    results = []

    while frontier:
        url, cur_depth = frontier.pop(0)
        if url in visited or cur_depth > depth:
            continue
        visited.add(url)
        html = fetch_url(url)
        if not html:
            continue
        meta = extract_meta(html)
        results.append({"url": url, "meta": meta})
        if cur_depth < depth:
            links = extract_links(html, start_url)
            for link in links:
                if link not in visited:
                    frontier.append((link, cur_depth + 1))
        time.sleep(delay)
    return results


def summarize_keywords(pages: List[Dict[str, Any]]) -> List[Dict[str, int]]:
    """Aggregate keyword frequencies across crawled pages."""
    counter = Counter()
    for page in pages:
        kw_str = page["meta"].get("keywords", "")
        if kw_str:
            for kw in kw_str.split(","):
                counter[kw.strip().lower()] += 1
    return [{"keyword": k, "count": c} for k, c in counter.most_common()]


def output_json(data: Any, out_path: Path):
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[+] Results written to {out_path}")

# --------------------------- CLI ---------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Lightweight competitor intelligence scraper – crawl a brand's public site and surface meta data & keyword trends."
    )
    p.add_argument("url", help="Root URL of the competitor site (e.g. https://example.com)")
    p.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth (default: 2)")
    p.add_argument("-o", "--output", type=Path, default=Path("competitor_report.json"), help="File to store JSON report")
    p.add_argument("-k", "--keywords", action="store_true", help="Include aggregated keyword summary")
    p.add_argument("-s", "--delay", type=float, default=1.0, help="Seconds to wait between requests (politeness)")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(f"[i] Starting crawl of {args.url} (depth={args.depth}) …")
    pages = crawl_site(args.url, depth=args.depth, delay=args.delay)

    report: Dict[str, Any] = {"site": args.url, "crawled_pages": len(pages), "pages": pages}
    if args.keywords:
        report["keyword_summary"] = summarize_keywords(pages)

    output_json(report, args.output)


if __name__ == "__main__":
    main()
