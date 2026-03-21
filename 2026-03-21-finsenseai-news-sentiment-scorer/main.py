import os
import requests
from transformers import pipeline
import torch 

class NewsSentimentAnalyzer:
    """
    Analyzes market sentiment from news headlines for a given stock ticker.
    Utilizes a pre-trained financial sentiment model from Hugging Face.
    """
    def __init__(self, news_api_key: str):
        if not news_api_key:
            raise ValueError("NEWS_API_KEY environment variable or argument is required.")
        self.news_api_key = news_api_key
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert", 
                tokenizer="ProsusAI/finbert",
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            print(f"Warning: Could not load FinBERT model, falling back to a general sentiment model. Error: {e}")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )


    def fetch_news_headlines(self, query: str, num_articles: int = 10) -> list[str]:
        """
        Fetches recent news headlines related to a query (e.g., stock ticker or company name).
        Uses NewsAPI.org.
        """
        url = f"https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "relevancy",
            "pageSize": num_articles,
            "language": "en",
            "apiKey": self.news_api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() 
            articles = response.json().get('articles', [])
            return [article['title'] for article in articles if article.get('title')]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for '{query}': {e}")
            return []

    def analyze_headlines_sentiment(self, headlines: list[str]) -> dict:
        """
        Analyzes the sentiment of a list of news headlines using the loaded NLP pipeline.
        Returns a dictionary with 'positive', 'negative', 'neutral' counts and scores.
        """
        if not headlines:
            return {"positive": 0, "negative": 0, "neutral": 0, "composite_score": 0.0, "details": []}

        sentiments_raw = self.sentiment_pipeline(headlines)
        
        normalized_sentiments = []
        for s in sentiments_raw:
            label = s['label'].lower()
            score = s['score']
            normalized_sentiments.append({'label': label, 'score': score})

        positive_scores = [s['score'] for s in normalized_sentiments if s['label'] == 'positive']
        negative_scores = [s['score'] for s in normalized_sentiments if s['label'] == 'negative']
        neutral_scores = [s['score'] for s in normalized_sentiments if s['label'] == 'neutral']

        total_articles = len(headlines)
        pos_count = len(positive_scores)
        neg_count = len(negative_scores)
        neu_count = len(neutral_scores)

        composite_score = 0.0
        if total_articles > 0:
            weighted_sum = sum(s['score'] for s in normalized_sentiments if s['label'] == 'positive') - \
                           sum(s['score'] for s in normalized_sentiments if s['label'] == 'negative')
            composite_score = weighted_sum / total_articles
        
        return {
            "positive_count": pos_count,
            "negative_count": neg_count,
            "neutral_count": neu_count,
            "total_headlines": total_articles,
            "composite_sentiment_score": round(composite_score, 4), 
            "details": [{"headline": h, "sentiment": s} for h, s in zip(headlines, normalized_sentiments)]
        }

    def get_market_sentiment(self, query: str, num_articles: int = 10) -> dict:
        """
        Orchestrates the process of fetching headlines and analyzing their sentiment.
        """
        print(f"Fetching news for: {query}...")
        headlines = self.fetch_news_headlines(query, num_articles)
        if not headlines:
            print("No headlines found or unable to fetch news.")
            return {"query": query, "message": "No data available for sentiment analysis."}

        print(f"Analyzing sentiment of {len(headlines)} headlines...")
        sentiment_results = self.analyze_headlines_sentiment(headlines)
        sentiment_results["query"] = query
        return sentiment_results

def main():
    NEWS_API_KEY = os.getenv("NEWS_API_KEY") 
    if not NEWS_API_KEY:
        print("Error: NEWS_API_KEY environment variable not set. Please get one from newsapi.org.")
        print("Example: export NEWS_API_KEY='YOUR_API_KEY'")
        return

    analyzer = NewsSentimentAnalyzer(news_api_key=NEWS_API_KEY)

    ticker = input("Enter stock ticker or company name (e.g., TSLA, Apple, NVIDIA): ").strip()
    if not ticker:
        print("No ticker entered. Exiting.")
        return

    results = analyzer.get_market_sentiment(ticker)

    if "message" in results:
        print(results["message"])
    else:
        print("\n--- FinSenseAI Market Sentiment Report ---")
        print(f"Query: {results['query']}")
        print(f"Total Headlines Analyzed: {results['total_headlines']}")
        print(f"Positive: {results['positive_count']} | Negative: {results['negative_count']} | Neutral: {results['neutral_count']}")
        print(f"Composite Sentiment Score (range -1 to 1): {results['composite_sentiment_score']:.4f}")
        print("\nTop Sentiment Headlines:")
        sorted_details = sorted(results['details'], key=lambda x: x['sentiment']['score'], reverse=True)
        
        print("\nStrongest Positive:")
        pos_printed = 0
        for detail in sorted_details:
            if detail['sentiment']['label'] == 'positive' and pos_printed < 3:
                print(f"  [{detail['sentiment']['label'].upper()} {detail['sentiment']['score']:.2f}] {detail['headline']}")
                pos_printed += 1
            if pos_printed == 3: break

        print("\nStrongest Negative:")
        neg_printed = 0
        for detail in sorted(sorted_details, key=lambda x: x['sentiment']['score']):
            if detail['sentiment']['label'] == 'negative' and neg_printed < 3:
                print(f"  [{detail['sentiment']['label'].upper()} {detail['sentiment']['score']:.2f}] {detail['headline']}")
                neg_printed += 1
            if neg_printed == 3: break
        
        print("\nNote: Score near 1 is strongly positive, near -1 is strongly negative.")
        print("       FinBERT model typically outputs 'positive', 'negative', 'neutral' labels.")

if __name__ == "__main__":
    main()