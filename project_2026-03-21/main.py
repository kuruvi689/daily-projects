import os
import json
import requests

# --- Configuration (config.py equivalent) ---
# Load API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM model to use
LLM_MODEL = "gpt-3.5-turbo" # Or "gpt-4" for higher quality, adjust cost accordingly

# --- Scraper Module (scraper.py equivalent) ---
def fetch_financial_news_mock():
    """
    Mocks fetching financial news articles. In a real system, this would
    scrape from various financial news sites, RSS feeds, or APIs.
    Returns a list of dictionaries, each with 'title' and 'content'.
    """
    mock_articles = [
        {
            "id": "news_001",
            "source": "Financial Times",
            "title": "Tech Giant X Reports Record Q3 Earnings, Shares Soar",
            "content": "Shares of Tech Giant X jumped 15% today after the company announced "
                       "better-than-expected third-quarter earnings, driven by strong "
                       "growth in its cloud computing division and successful product launches. "
                       "Analysts raised their price targets significantly."
        },
        {
            "id": "news_002",
            "source": "Wall Street Journal",
            "title": "Global Supply Chain Disruptions Continue to Hit Manufacturing Sector",
            "content": "Manufacturers worldwide are grappling with persistent supply chain "
                       "issues, leading to production delays and increased costs. "
                       "This could impact profitability for several industries through year-end."
        },
        {
            "id": "news_003",
            "source": "Reuters",
            "title": "New Interest Rate Hike Expected as Inflation Concerns Mount",
            "content": "Economists widely anticipate another interest rate hike by the central bank "
                       "next month, as inflationary pressures show little sign of easing. "
                       "This move aims to cool down the economy but could dampen consumer spending."
        },
        {
            "id": "news_004",
            "source": "Bloomberg",
            "title": "Biotech Startup Y Secures Major Funding Round for Cancer Research",
            "content": "Biotech Startup Y announced a successful Series B funding round, "
                       "securing $100 million to accelerate its groundbreaking cancer research. "
                       "The investment highlights growing confidence in novel therapeutic approaches."
        }
    ]
    print(f"[{__name__}] Fetched {len(mock_articles)} mock financial news articles.")
    return mock_articles

# --- Analyzer Module (analyzer.py equivalent) ---
def analyze_sentiment_with_llm(text: str) -> dict:
    """
    Uses an LLM to analyze the sentiment of a given text.
    Returns a dictionary with 'sentiment' (e.g., 'positive', 'negative', 'neutral')
    and 'score' (e.g., -1 to 1).
    """
    if not OPENAI_API_KEY:
        return {"sentiment": "error", "score": 0.0, "reason": "OPENAI_API_KEY environment variable not set."}

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a financial sentiment analysis expert. Analyze the "
                        "sentiment of the provided news text for its impact on financial markets "
                        "or specific entities mentioned. Respond with a JSON object "
                        "containing 'sentiment' (positive, negative, neutral) and a 'score' "
                        "(a float between -1.0 for very negative and 1.0 for very positive). "
                        "Also include a 'reason' explaining your sentiment based on the text."
                    )
                },
                {"role": "user", "content": text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0 # Keep it deterministic for sentiment
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        response_data = response.json()
        
        # Extract the JSON string from the LLM response
        llm_output_str = response_data['choices'][0]['message']['content']
        llm_sentiment = json.loads(llm_output_str)

        # Validate the LLM's output structure
        if "sentiment" not in llm_sentiment or "score" not in llm_sentiment:
            print(f"[{__name__}] LLM returned unexpected format: {llm_sentiment}")
            return {"sentiment": "neutral", "score": 0.0, "reason": "LLM output format error."}
        
        return llm_sentiment

    except requests.exceptions.RequestException as e:
        print(f"[{__name__}] API request failed: {e}")
        return {"sentiment": "error", "score": 0.0, "reason": f"API request error: {e}"}
    except json.JSONDecodeError as e:
        print(f"[{__name__}] Failed to parse LLM JSON response: {e}")
        return {"sentiment": "error", "score": 0.0, "reason": f"LLM response JSON parsing error: {e}"}
    except Exception as e:
        print(f"[{__name__}] An unexpected error occurred during sentiment analysis: {e}")
        return {"sentiment": "error", "score": 0.0, "reason": f"Unexpected error: {e}"}


# --- Aggregator Module (aggregator.py equivalent) ---
def aggregate_sentiment_results(analyzed_articles: list) -> dict:
    """
    Aggregates sentiment results from multiple articles.
    Calculates overall sentiment, average score, and counts per sentiment type.
    """
    total_score = 0
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "error": 0}
    
    for article in analyzed_articles:
        score = article.get("sentiment_result", {}).get("score", 0.0)
        sentiment_type = article.get("sentiment_result", {}).get("sentiment", "neutral").lower()
        
        total_score += score
        sentiment_counts[sentiment_type] = sentiment_counts.get(sentiment_type, 0) + 1

    num_articles = len(analyzed_articles)
    if num_articles == 0:
        return {
            "overall_sentiment": "neutral",
            "average_score": 0.0,
            "sentiment_distribution": sentiment_counts,
            "total_articles": 0
        }

    average_score = total_score / num_articles
    
    if average_score > 0.1:
        overall_sentiment = "generally positive"
    elif average_score < -0.1:
        overall_sentiment = "generally negative"
    else:
        overall_sentiment = "mixed/neutral"

    return {
        "overall_sentiment": overall_sentiment,
        "average_score": round(average_score, 4),
        "sentiment_distribution": sentiment_counts,
        "total_articles": num_articles
    }

# --- Main Orchestrator (main.py equivalent) ---
def run_fin_sense_ai():
    """
    Orchestrates the entire process: fetching news, analyzing sentiment, and aggregating results.
    """
    print("[FinSenseAI] Starting financial news sentiment analysis...")

    # 1. Fetch news
    articles = fetch_financial_news_mock()
    if not articles:
        print("[FinSenseAI] No articles fetched. Exiting.")
        return

    # 2. Analyze sentiment for each article
    analyzed_articles = []
    for article in articles:
        print(f"[FinSenseAI] Analyzing sentiment for: '{article['title']}'...")
        sentiment_result = analyze_sentiment_with_llm(article['content'])
        article['sentiment_result'] = sentiment_result
        analyzed_articles.append(article)
        
    # 3. Aggregate results
    final_aggregation = aggregate_sentiment_results(analyzed_articles)

    print("\n--- Individual Article Analysis ---")
    for article in analyzed_articles:
        print(f"Title: {article['title']}")
        print(f"  Sentiment: {article['sentiment_result'].get('sentiment', 'N/A')} "
              f"(Score: {article['sentiment_result'].get('score', 'N/A'):.2f})")
        print(f"  Reason: {article['sentiment_result'].get('reason', 'N/A')}\n")

    print("\n--- Overall Market Sentiment Summary ---")
    print(json.dumps(final_aggregation, indent=4))

    # Optional: Save results to a JSON file
    output_filename = "fin_sense_ai_results.json"
    with open(output_filename, 'w') as f:
        json.dump({
            "individual_articles": analyzed_articles,
            "overall_summary": final_aggregation
        }, f, indent=4)
    print(f"\n[FinSenseAI] Results saved to {output_filename}")


if __name__ == "__main__":
    run_fin_sense_ai()
