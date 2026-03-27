import requests
from bs4 import BeautifulSoup
import re
import random
import time

# --- MOCK LLM INTEGRATION ---
class MockLLMSentiment:
    """
    A mock LLM for sentiment analysis. In a real scenario, this would
    interface with an actual LLM API (e.g., OpenAI, Hugging Face).
    """
    def __init__(self, api_key=None):
        self.api_key = api_key # Placeholder for actual API key usage

    def _call_llm_api(self, prompt: str) -> str:
        """Simulates an API call to an LLM."""
        time.sleep(0.5) # Simulate network latency
        # Simple rule-based mock for demonstration
        if "positive" in prompt.lower() or "growth" in prompt.lower() or "optimistic" in prompt.lower() or "record" in prompt.lower():
            return f"Sentiment: Positive, Score: {random.uniform(0.7, 0.95):.2f}"
        elif "negative" in prompt.lower() or "decline" in prompt.lower() or "pessimistic" in prompt.lower() or "slowdown" in prompt.lower() or "concerns" in prompt.lower():
            return f"Sentiment: Negative, Score: {random.uniform(0.6, 0.85):.2f}"
        else:
            return f"Sentiment: Neutral, Score: {random.uniform(0.1, 0.4):.2f}"

    def analyze_text(self, text: str) -> dict:
        """
        Analyzes the sentiment of a given text using the mock LLM.
        In a real LLM integration, the prompt would be crafted carefully.
        """
        prompt = f"Analyze the sentiment of the following financial news article text and provide a single sentiment (Positive, Negative, Neutral) and a score (0.0 to 1.0): '{text[:500]}...'"
        llm_response = self._call_llm_api(prompt)

        # Parse the mock LLM's response
        sentiment_match = re.search(r"Sentiment: (Positive|Negative|Neutral)", llm_response)
        score_match = re.search(r"Score: ([\d.]+)", llm_response)

        sentiment = sentiment_match.group(1) if sentiment_match else "Neutral"
        score = float(score_match.group(1)) if score_match else 0.0

        return {"sentiment": sentiment, "score": score}

# --- FINANCIAL NEWS SCRAPER ---
class FinancialNewsScraper:
    """
    A modular scraper for financial news.
    Designed to be extensible for various news sources.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _fetch_page_content(self, url: str) -> str:
        """Fetches the raw HTML content of a given URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def scrape_article(self, url: str) -> dict:
        """
        Scrapes a single article from a given URL, extracting title and main content.
        This is a generic approach; specific sites might need custom parsers.
        """
        html_content = self._fetch_page_content(url)
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')

        # Attempt to find article title
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "No Title Found"

        # Attempt to find main article content heuristics
        article_body = soup.find('article') or soup.find('div', class_=re.compile(r'content|body|article', re.IGNORECASE))
        
        paragraphs = []
        if article_body:
            paragraphs = article_body.find_all('p')
        else: # Fallback to finding all paragraphs if no specific article body is found
            paragraphs = soup.find_all('p')
            
        content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        return {"url": url, "title": title, "content": content}

# --- ORCHESTRATOR ---
class FinSenseScout:
    """
    Orchestrates financial news scraping and sentiment analysis.
    """
    def __init__(self):
        self.scraper = FinancialNewsScraper()
        self.sentiment_analyzer = MockLLMSentiment() # In production, use a real LLM client

    def analyze_news_source(self, urls: list[str]) -> list[dict]:
        """
        Fetches articles from a list of URLs, analyzes their sentiment,
        and returns structured results.
        """
        results = []
        for url in urls:
            print(f"Scraping: {url}")
            article_data = self.scraper.scrape_article(url)
            if article_data and article_data["content"]:
                print(f"Analyzing sentiment for '{article_data['title']}'...")
                sentiment_data = self.sentiment_analyzer.analyze_text(article_data["content"])
                
                results.append({
                    "url": article_data["url"],
                    "title": article_data["title"],
                    "sentiment": sentiment_data["sentiment"],
                    "score": sentiment_data["score"],
                    "summary_preview": article_data["content"][:200] + "..." if len(article_data["content"]) > 200 else article_data["content"]
                })
                time.sleep(0.2) # Be kind to servers and LLM rate limits
            else:
                print(f"Could not scrape content from {url}. Skipping sentiment analysis.")
        return results

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Example usage:
    # For a real-world application, this would fetch from a list of known financial news sources
    # or an RSS feed. Using example URLs here.
    
    # Note: Live scraping can be fragile due to website changes or anti-scraping measures.
    # These URLs are illustrative and may require updates or more robust handling.

    example_news_urls = [
        "https://www.cnbc.com/2024/03/27/stocks-making-the-biggest-moves-midday-tesla-gamestop-more.html",
        "https://www.reuters.com/markets/europe/europes-stoxx-600-hits-record-high-tech-sector-leads-2024-03-27/",
        "https://www.bloomberg.com/news/articles/2024-03-27/asia-stocks-set-to-rise-after-us-tech-rally-markets-wrap",
    ]

    # Mock articles for robust testing or if live scraping fails.
    mock_positive_article = {
        "url": "https://example.com/positive-growth-news",
        "title": "Tech Giant Reports Record Earnings and Optimistic Outlook",
        "content": "A leading technology firm today announced record-breaking quarterly earnings, exceeding analyst expectations with strong revenue growth and expanded profit margins. The CEO expressed optimism about future market expansion and innovative product development. Investors reacted positively, with shares surging by 15%."
    }
    mock_negative_article = {
        "url": "https://example.com/economic-slowdown-concerns",
        "title": "Economic Outlook Worsens Amid Inflation Fears",
        "content": "New economic data suggests a potential slowdown in global growth, with inflation remaining stubbornly high. Central bank officials indicated a cautious approach, raising concerns among investors about market stability. Analysts foresee potential declines in consumer spending and corporate profits for the upcoming quarter."
    }
    
    app = FinSenseScout()
    
    analyzed_articles = []
    # Attempt to scrape and analyze the live URLs first
    try:
        live_analyzed = app.analyze_news_source(example_news_urls)
        analyzed_articles.extend(live_analyzed)
    except Exception as e:
        print(f"An error occurred during live scraping: {e}")

    # If no live articles were successfully analyzed, or for supplementing:
    if not analyzed_articles or len(analyzed_articles) < 2: # Ensure at least two articles for demo
        print("\nSupplementing with mock data for demonstration purposes...")
        # Directly process mock content for sentiment analysis
        analyzed_articles.append({
            "url": mock_positive_article["url"],
            "title": mock_positive_article["title"],
            **app.sentiment_analyzer.analyze_text(mock_positive_article["content"]),
            "summary_preview": mock_positive_article["content"][:200] + "..."
        })
        analyzed_articles.append({
            "url": mock_negative_article["url"],
            "title": mock_negative_article["title"],
            **app.sentiment_analyzer.analyze_text(mock_negative_article["content"]),
            "summary_preview": mock_negative_article["content"][:200] + "..."
        })

    print("\n--- FinSenseScout Analysis Report ---")
    if not analyzed_articles:
        print("No articles could be scraped or mocked. Please check URLs or mock data logic.")
    for article in analyzed_articles:
        print(f"\nTitle: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Sentiment: {article['sentiment']} (Score: {article['score']:.2f})")
        print(f"Preview: {article['summary_preview']}")
        print("-" * 50)
