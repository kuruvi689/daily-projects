import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

# ---------------------------- Core Logic ----------------------------

def fetch_url(url: str, timeout: int = 10) -> str:
    """Return raw HTML of *url* or raise a descriptive exception."""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}")


def parse_meta(html: str) -> Dict[str, str]:
    """Extract title and meta description from *html*.
    Returns a dict with keys: title, description (empty string if missing)."""
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
    return {"title": title, "description": description}


def analyze_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """Run fetch + parse for a list of URLs.
    Returns a list of dicts with url, title, description, and any error message."""
    results = []
    for url in urls:
        entry: Dict[str, Any] = {"url": url}
        try:
            html = fetch_url(url)
            meta = parse_meta(html)
            entry.update(meta)
            entry["error"] = ""
        except Exception as exc:
            entry.update({"title": "", "description": "", "error": str(exc)})
        results.append(entry)
    return results

# ---------------------------- CLI ----------------------------

def load_urls(source: Path) -> List[str]:
    """Load URLs from a JSON or plain‑text file.
    *JSON* – expects an array of strings.
    *TXT* – one URL per line, blank lines ignored.
    """
    if not source.is_file():
        raise FileNotFoundError(f"Input file {source} does not exist")
    if source.suffix.lower() == ".json":
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list of URLs")
        return [str(item).strip() for item in data if str(item).strip()]
    else:
        return [line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def output_results(results: List[Dict[str, Any]], dest: Path, fmt: str) -> None:
    fmt = fmt.lower()
    if fmt == "json":
        dest.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    elif fmt == "csv":
        import csv
        fieldnames = ["url", "title", "description", "error"]
        with dest.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
    else:
        raise ValueError("Unsupported output format: choose 'json' or 'csv'")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="market-visibility-analyzer",
        description="CLI tool that fetches a list of competitor URLs and extracts their page title and meta description. Useful for quick market‑visibility audits and can be wrapped as a micro‑service.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a file containing URLs (one per line or a JSON array).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("visibility-report.json"),
        help="Destination file for the report (default: visibility-report.json).",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format – json (default) or csv.",
    )
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        urls = load_urls(args.input)
        if not urls:
            sys.exit("No URLs found in the input file.")
        results = analyze_urls(urls)
        output_results(results, args.output, args.format)
        print(f"Report written to {args.output} ({args.format.upper()})")
    except Exception as exc:
        sys.exit(str(exc))

if __name__ == "__main__":
    main()
