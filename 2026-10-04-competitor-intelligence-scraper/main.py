#!/usr/bin/env python3
"""competitor-intelligence-scraper

A lightweight CLI that scrapes competitor product pages for key attributes
(e.g. price, title, rating) and outputs a CSV for analysis.

Usage:
  python main.py --url https://example.com/product/123 --output data.csv

The script focuses on a single product page per run but can be extended to
crawl multiple URLs. It uses only the standard library and two small
dependencies: requests and beautifulsoup4.
"""

import argparse
import csv
import json
import sys
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

@dataclass
class ProductInfo:
    url: str
    title: Optional[str] = None
    price: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    tags: List[str] = None

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title or "",
            "price": self.price or "",
            "rating": self.rating if self.rating is not None else "",
            "reviews": self.reviews if self.reviews is not None else "",
            "tags": ",".join(self.tags or []),
        }

def fetch_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CI-Scraper/1.0)"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text

# Simple heuristics for common e‑commerce sites.
# In practice, this would be a plug‑in system.

def parse_product(html: str, url: str) -> ProductInfo:
    soup = BeautifulSoup(html, "html.parser")
    prod = ProductInfo(url=url)

    # Title
    title_tag = soup.find("h1") or soup.find("h1", class_="title")
    prod.title = title_tag.get_text(strip=True) if title_tag else None

    # Price
    price_tag = soup.find("span", class_=re.compile("price|amount|cost"))
    prod.price = price_tag.get_text(strip=True) if price_tag else None

    # Rating
    rating_tag = soup.find("span", class_=re.compile("rating|stars"))
    if rating_tag:
        m = re.search(r"([0-5](?:\.[0-9])?)", rating_tag.get_text())
        prod.rating = float(m.group(1)) if m else None

    # Reviews count
    rev_tag = soup.find("span", class_=re.compile("review[s]?"))
    if rev_tag:
        m = re.search(r"([0-9,]+)", rev_tag.get_text())
        if m:
            prod.reviews = int(m.group(1).replace(",", ""))

    # Tags / categories
    tags = []
    for li in soup.select("ul.breadcrumb li a"):
        tags.append(li.get_text(strip=True))
    prod.tags = tags or None

    return prod

def write_csv(products: List[ProductInfo], path: Path):
    fieldnames = ["url", "title", "price", "rating", "reviews", "tags"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow(p.to_dict())


def main():
    parser = argparse.ArgumentParser(description="Competitor intelligence scraper")
    parser.add_argument("--url", required=True, help="Product page URL to scrape")
    parser.add_argument("--output", default="product.csv", help="Output CSV file")
    args = parser.parse_args()

    try:
        html = fetch_page(args.url)
        prod = parse_product(html, args.url)
        write_csv([prod], Path(args.output))
        print(f"Scraped data written to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
