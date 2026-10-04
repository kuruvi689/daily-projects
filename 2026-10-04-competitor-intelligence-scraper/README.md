# Competitor Intelligence Scraper

A lightweight, command‑line tool that extracts key product attributes from a competitor’s web page – price, title, rating, review count, and tags – and outputs a CSV for strategic analysis.

## Why It Matters
- **Fast, repeatable data collection** for pricing and feature comparison.
- **SaaS‑ready**: Wrap the CLI in a simple API, charge a low monthly fee, and serve SMEs.
- **Modular**: The core parsing logic can be imported into larger systems or extended with plug‑in extractors.
- **Zero‑GPU, Windows‑friendly**: Runs on a standard Windows laptop with only `requests` and `beautifulsoup4`.

## Features
- One‑page extraction, but can be looped for lists of URLs.
- Heuristic parsing for common e‑commerce layouts.
- CSV output – ready for Excel, PowerBI, or any downstream tool.

## Installation
```bash
pip install requests beautifulsoup4
```

## Usage
```bash
python main.py --url https://example.com/product/123 --output data.csv
```

## Extending
- Add more `parse_product` heuristics for other sites.
- Replace the CSV writer with a database writer for a full SaaS backend.

## Tags
#AIMastery #Strategy #Finance
