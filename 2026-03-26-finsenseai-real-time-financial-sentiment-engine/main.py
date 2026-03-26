import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import openai
from dotenv import load_dotenv
import time
import json

# Load environment variables from .env file
load_dotenv()

class ArticleScraper:
    """
    A modular class to scrape articles from given URLs or RSS feeds.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _extract_text_from_html(self, html_content):
        if not html_content:
            return None
        soup = BeautifulSoup(html_content, 'html.parser')
        # Common tags for article content, prioritize main content areas
        main_content_div = soup.find('div', class_=['article-body', 'entry-content', 'td-post-content', 'story-body', 'post-content'])
        if main_content_div:
            paragraphs = main_content_div.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        else:
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])

        text = "\n".join([p.get_text() for p in paragraphs])
        return text.strip()

    def scrape_article(self, url):
        """Scrapes a single article URL and returns its cleaned text content."""
        print(f"Scraping article from: {url}")
        html_content = self._get_html(url)
        if html_content:
            return self._extract_text_from_html(html_content)
        return None

    def scrape_rss_feed(self, rss_url, limit=5):
        """Scrapes articles from an RSS feed."""
        print(f"Scraping RSS feed: {rss_url}")
        html_content = self._get_html(rss_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'xml') # RSS is XML
        articles_data = []
        for item in soup.find_all('item')[:limit]:
            link = item.find('link').text if item.find('link') else None
            title = item.find('title').text if item.find('title') else 'No Title'
            pub_date = item.find('pubDate').text if item.find('pubDate') else 'No Date'
            
            if link and link not in [a['url'] for a in articles_data]: # Avoid duplicates within a run
                article_text = self.scrape_article(link)
                if article_text:
                    articles_data.append({
                        'title': title,
                        'url': link,
                        'published_date': pub_date,
                        'content': article_text
                    })
            time.sleep(1) # Be polite to servers
        return articles_data

class LLMSentimentAnalyzer:
    """
    A modular class to analyze text sentiment using an LLM.
    """
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        if not self.client.api_key:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your .env file or pass it to the constructor.")

    def analyze_sentiment(self, text):
        """
        Analyzes the sentiment of a given text using the configured LLM.
        Returns a dictionary with 'sentiment' (positive/negative/neutral) and 'score' (-1 to 1).
        """
        if not text:
            return {"sentiment": "neutral", "score": 0.0, "summary": "No text provided."}

        # Truncate text to fit within typical LLM context windows and save tokens
        truncated_text = text[:3000] if len(text) > 3000 else text 

        prompt = f"""Analyze the sentiment of the following financial news article snippet.
        Provide a single word sentiment (Positive, Negative, Neutral) and a numerical score from -1.0 (strongly negative) to 1.0 (strongly positive).
        Also, provide a brief summary (1-2 sentences) focusing on the key financial implications.
        Focus solely on the financial implications mentioned in the text.

        Text: """{truncated_text}"""

        Format your response as a JSON object with 'sentiment', 'score', and 'summary' keys.
        Example: {{"sentiment": "Positive", "score": 0.85, "summary": "Company stock expected to rise due to strong earnings."}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analysis AI, providing concise and accurate financial sentiment and summaries."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2, # Keep low for consistent sentiment
                max_tokens=300 # Sufficient for JSON output and summary
            )
            
            sentiment_data_str = response.choices[0].message.content
            # Ensure it's valid JSON
            sentiment_json = json.loads(sentiment_data_str)
            # Validate structure, provide defaults if keys are missing
            return {
                "sentiment": sentiment_json.get("sentiment", "neutral"),
                "score": float(sentiment_json.get("score", 0.0)),
                "summary": sentiment_json.get("summary", "No summary provided.")
            }

        except json.JSONDecodeError as e:
            print(f"LLM returned invalid JSON: {sentiment_data_str} - Error: {e}")
            return {"sentiment": "error", "score": 0.0, "summary": f"Invalid JSON from LLM: {e}"}
        except Exception as e:
            print(f"Error during LLM sentiment analysis: {e}")
            return {"sentiment": "error", "score": 0.0, "summary": str(e)}

class SentimentDatabase:
    """
    A modular class for managing sentiment data storage in SQLite.
    """
    def __init__(self, db_name="finsense_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT UNIQUE,
                published_date TEXT,
                content TEXT,
                sentiment TEXT,
                score REAL,
                summary TEXT,
                analysis_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_article_sentiment(self, article_data, sentiment_data):
        """Inserts a new article's sentiment data."""
        try:
            self.cursor.execute("""
                INSERT INTO articles (title, url, published_date, content, sentiment, score, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                article_data.get('title'),
                article_data.get('url'),
                article_data.get('published_date'),
                article_data.get('content'),
                sentiment_data.get('sentiment'),
                sentiment_data.get('score'),
                sentiment_data.get('summary')
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Article with URL '{article_data.get('url')}' already exists. Skipping.")
            return False
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    def get_all_sentiment_data(self):
        """Retrieves all stored sentiment data."""
        self.cursor.execute("SELECT * FROM articles ORDER BY analysis_date DESC")
        # Optionally, convert rows to dicts for easier consumption
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def close(self):
        """Closes the database connection."""
        self.conn.close()

def main():
    print("--- FinSenseAI: Real-Time Financial Sentiment Engine ---")

    scraper = ArticleScraper()
    try:
        analyzer = LLMSentimentAnalyzer()
    except ValueError as e:
        print(f"Initialization error: {e}")
        print("Please ensure your OPENAI_API_KEY is correctly set in the .env file.")
        return

    db = SentimentDatabase()

    # Configure RSS feeds. Add relevant financial news RSS feeds here.
    # Examples of reputable financial news RSS feeds:
    # Reuters: http://feeds.reuters.com/reuters/businessNews
    # Bloomberg: https://www.bloomberg.com/feed/bpol/articles/rss.xml (often not working without specific user-agent/subscription)
    # Financial Times (requires subscription for full content):
    FINANCIAL_RSS_FEEDS = [
        "http://feeds.reuters.com/reuters/businessNews",
        # "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
        # Add more financial RSS feeds here to expand coverage
    ]

    if not FINANCIAL_RSS_FEEDS:
        print("Warning: No RSS feeds configured. Please add URLs to FINANCIAL_RSS_FEEDS.")

    for feed_url in FINANCIAL_RSS_FEEDS:
        articles_to_process = scraper.scrape_rss_feed(feed_url, limit=3) # Limit per feed for quick testing and politeness

        for article in articles_to_process:
            print(f"\nProcessing: {article['title']}")
            if article['content']:
                sentiment_result = analyzer.analyze_sentiment(article['content'])
                print(f"  Sentiment: {sentiment_result.get('sentiment')}, Score: {sentiment_result.get('score')}")
                print(f"  Summary: {sentiment_result.get('summary')}")
                
                db.insert_article_sentiment(article, sentiment_result)
            else:
                print(f"  No content extracted for {article['url']}. Skipping sentiment analysis.")
            time.sleep(2) # Be polite to LLM API and avoid rate limits

    print("\n--- Sentiment Analysis Complete. Data stored in finsense_data.db ---")
    
    # Example: Retrieve and print some data
    print("\nRecent sentiment entries:")
    for entry in db.get_all_sentiment_data()[:5]: # Print top 5 recent entries
        print(f"Title: {entry['title']}\nURL: {entry['url']}\nSentiment: {entry['sentiment']} (Score: {entry['score']})\nSummary: {entry['summary']}\n")

    db.close()

if __name__ == "__main__":
    main()
