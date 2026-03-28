import os
from dotenv import load_dotenv
import openai
import json

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Using OpenAI as the LLM provider for demonstration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

openai.api_key = OPENAI_API_KEY

# --- Modular Component 1: Data Fetcher (Mock for demonstration) ---
class DataFetcher:
    """
    Simulates fetching financial news articles. In a real-world scenario,
    this would integrate with news APIs (e.g., Alpha Vantage, NewsAPI, Bloomberg).
    """
    def fetch_articles_for_sector(self, sector: str, count: int = 3) -> list[dict]:
        print(f"[DataFetcher] Simulating fetching {count} articles for '{sector}'...")
        # Mock data - replace with actual API calls
        mock_articles = {
            "Tech": [
                {
                    "title": "Quantum Computing Breakthrough Propels Tech Sector",
                    "content": "Scientists announced a significant leap in quantum computing, creating a buzz across the tech industry and sending stock prices for related companies soaring. Analysts predict massive long-term growth."
                },
                {
                    "title": "AI Regulation Concerns Weigh on Big Tech Giants",
                    "content": "New regulatory proposals targeting AI governance have raised concerns among major tech companies, potentially impacting innovation and market expansion. Shares saw a slight dip."
                },
                {
                    "title": "Semiconductor Shortages Continue to Challenge Tech Production",
                    "content": "The persistent global semiconductor shortage is still hampering production in the tech sector, leading to delayed product launches and revenue warnings from several manufacturers."
                },
                {
                    "title": "Metaverse Investments See Mixed Returns for Early Adopters",
                    "content": "While some companies report promising early results from metaverse ventures, others are scaling back, citing high development costs and uncertain user adoption rates. The future remains speculative."
                }
            ],
            "Finance": [
                {
                    "title": "Central Bank Signals Rate Hikes Amid Inflationary Pressures",
                    "content": "The central bank indicated further interest rate hikes are likely to combat persistent inflation, impacting borrowing costs for consumers and businesses. Banks may benefit from wider margins."
                },
                {
                    "title": "Fintech Startup Achieves Unicorn Status with Disruptive Payment Solution",
                    "content": "A new fintech company secured a valuation over $1 billion after launching an innovative payment processing platform, challenging traditional banking models."
                },
                {
                    "title": "Global Banking Sector Navigates Geopolitical Risks and Market Volatility",
                    "content": "International banks are facing increased scrutiny and uncertainty due to escalating geopolitical tensions and erratic market movements, potentially affecting cross-border transactions and investment strategies."
                },
                {
                    "title": "Cryptocurrency Adoption Grows, Posing Opportunities and Challenges for Traditional Finance",
                    "content": "The increasing mainstream acceptance of cryptocurrencies presents both new revenue streams and regulatory hurdles for established financial institutions looking to integrate digital assets."
                }
            ]
        }
        
        # Filter articles for the specified sector and return the requested count
        return mock_articles.get(sector, [])[:count]

# --- Modular Component 2: Sentiment Analyzer ---
class LLMSentimentAnalyzer:
    """
    Analyzes the sentiment of a given text using an LLM.
    """
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model

    def analyze_sentiment(self, text: str) -> dict:
        print(f"[LLMSentimentAnalyzer] Analyzing text: {text[:50]}...")
        prompt = f"""
        Analyze the sentiment of the following financial news article snippet for its impact on the specified sector.
        Provide a sentiment score from -1 (very negative) to 1 (very positive), and a brief justification.
        Also, identify 1-2 key themes mentioned in the article affecting the sector.

        Output format must be a JSON object with 'score' (float), 'justification' (string), and 'themes' (list of strings).

        Article: """{text}"""
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial news sentiment analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3 # Keep sentiment analysis relatively consistent
            )
            content = response.choices[0].message['content']
            # Attempt to parse the JSON output
            sentiment_data = json.loads(content)
            return sentiment_data
        except json.JSONDecodeError:
            print(f"[LLMSentimentAnalyzer ERROR] Failed to decode JSON from LLM: {content}")
            return {"score": 0.0, "justification": "LLM output format error.", "themes": []}
        except Exception as e:
            print(f"[LLMSentimentAnalyzer ERROR] An error occurred during LLM call: {e}")
            return {"score": 0.0, "justification": f"LLM API error: {e}", "themes": []}

# --- Modular Component 3: Report Generator ---
class SectorSentimentReporter:
    """
    Aggregates sentiment data and generates a structured report.
    """
    def generate_report(self, sector: str, analyzed_articles: list[dict]) -> dict:
        print(f"[SectorSentimentReporter] Generating report for '{sector}'...")
        if not analyzed_articles:
            return {
                "sector": sector,
                "overall_sentiment_score": 0.0,
                "overall_justification": "No articles analyzed.",
                "key_themes_identified": [],
                "detailed_analysis": []
            }

        total_score = 0.0
        all_justifications = []
        all_themes = set()
        detailed_analysis = []

        for article_data in analyzed_articles:
            sentiment_result = article_data.get("sentiment_result", {})
            total_score += sentiment_result.get("score", 0.0)
            all_justifications.append(sentiment_result.get("justification", "N/A"))
            for theme in sentiment_result.get("themes", []):
                all_themes.add(theme)
            
            detailed_analysis.append({
                "title": article_data.get("title", "No Title"),
                "sentiment_score": sentiment_result.get("score", 0.0),
                "justification": sentiment_result.get("justification", "N/A"),
                "themes": sentiment_result.get("themes", [])
            })

        overall_score = total_score / len(analyzed_articles)
        
        # Simple aggregation for overall justification
        overall_justification = f"Based on {len(analyzed_articles)} articles, the sector shows an average sentiment of {overall_score:.2f}. Key influences include {', '.join(list(all_themes)[:3]) or 'various factors'}."

        return {
            "sector": sector,
            "overall_sentiment_score": round(overall_score, 2),
            "overall_justification": overall_justification,
            "key_themes_identified": sorted(list(all_themes)),
            "detailed_analysis": detailed_analysis
        }

# --- Orchestrator --- 
def main():
    """
    Orchestrates the data fetching, sentiment analysis, and report generation.
    """
    target_sectors = ["Tech", "Finance"]
    num_articles_per_sector = 2 # Keep low for faster demo/cost control

    fetcher = DataFetcher()
    analyzer = LLMSentimentAnalyzer()
    reporter = SectorSentimentReporter()

    for sector in target_sectors:
        print(f"\n=== Processing Sector: {sector} ===")
        articles = fetcher.fetch_articles_for_sector(sector, num_articles_per_sector)
        
        analyzed_articles = []
        for article in articles:
            sentiment_result = analyzer.analyze_sentiment(article["content"])
            article["sentiment_result"] = sentiment_result
            analyzed_articles.append(article)

        report = reporter.generate_report(sector, analyzed_articles)
        print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()
