import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# Optional external deps – keep minimal
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    print('Required packages not installed. Run: pip install requests beautifulsoup4')
    sys.exit(1)

DEFAULT_DAYS = 7
CACHE_DIR = Path('.cache')
CACHE_DIR.mkdir(exist_ok=True)

def fetch_rss(url: str) -> str:
    """Download RSS XML, with a tiny on‑disk cache to avoid hammering the source."""
    cache_file = CACHE_DIR / (url.replace('://', '_').replace('/', '_') + '.xml')
    if cache_file.exists() and (time.time() - cache_file.stat().st_mtime) < 3600:
        return cache_file.read_text(encoding='utf-8')
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    cache_file.write_text(resp.text, encoding='utf-8')
    return resp.text

def parse_bing_news(company: str, days: int = DEFAULT_DAYS) -> List[Dict[str, str]]:
    """Fetch recent news for *company* via Bing News RSS.
    Returns a list of dicts with 'title', 'link', and 'pubDate' (ISO string)."""
    query = f"{company} news"
    rss_url = f"https://www.bing.com/news/search?q={requests.utils.quote(query)}&format=rss"
    xml = fetch_rss(rss_url)
    soup = BeautifulSoup(xml, 'xml')
    items = []
    cutoff = datetime.utcnow() - timedelta(days=days)
    for entry in soup.find_all('item'):
        pub = entry.pubDate.text if entry.pubDate else ''
        try:
            pub_dt = datetime.strptime(pub, '%a, %d %b %Y %H:%M:%S %Z')
        except Exception:
            continue
        if pub_dt < cutoff:
            continue
        items.append({
            'title': entry.title.text,
            'link': entry.link.text,
            'pubDate': pub_dt.isoformat()
        })
    return items

def keyword_score(text: str, keywords: List[str]) -> int:
    """Simple relevance score – count of keyword occurrences (case‑insensitive)."""
    lowered = text.lower()
    return sum(lowered.count(k.lower()) for k in keywords)

def analyse(company: str, keywords: List[str], days: int) -> Tuple[List[Dict], int, Counter]:
    news = parse_bing_news(company, days)
    scored = []
    total_score = 0
    keyword_counter = Counter()
    for item in news:
        score = keyword_score(item['title'] + ' ' + item.get('description', ''), keywords)
        total_score += score
        scored.append({**item, 'score': score})
        for kw in keywords:
            if kw.lower() in (item['title'] + ' ' + item.get('description', '')).lower():
                keyword_counter[kw] += 1
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored, total_score, keyword_counter

def save_report(report: Dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

def cli() -> None:
    parser = argparse.ArgumentParser(
        description='Strategic Leverage Matrix – lightweight competitor intel CLI')
    parser.add_argument('company', help='Target company or brand name')
    parser.add_argument('--keywords', '-k', nargs='*', default=[], help='Focus keywords (e.g., pricing, partnership)')
    parser.add_argument('--days', '-d', type=int, default=DEFAULT_DAYS, help='Look‑back window in days')
    parser.add_argument('--output', '-o', type=Path, default=Path('leverage_report.json'), help='JSON report file')
    args = parser.parse_args()

    if not args.keywords:
        print('No keywords supplied – using generic strategic terms')
        args.keywords = ['price', 'partnership', 'acquisition', 'launch', 'regulation']

    print(f'Fetching news for {args.company} (last {args.days} days)…')
    scored, total, kw_counts = analyse(args.company, args.keywords, args.days)

    report = {
        'company': args.company,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'lookback_days': args.days,
        'keywords': args.keywords,
        'total_relevance_score': total,
        'keyword_hits': dict(kw_counts),
        'top_items': scored[:10]  # expose only the most relevant headlines
    }
    save_report(report, args.output)
    print(f'Report saved to {args.output}')
    print('\nTop 5 items:')
    for item in report['top_items'][:5]:
        print(f"- [{item['score']}] {item['title']} ({item['pubDate'][:10]})")

if __name__ == '__main__':
    cli()
