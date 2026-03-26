import os
import requests
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Suppress UserWarnings from HuggingFace tokenizers, etc.
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

class NewsFetcher:
    """
    Fetches financial news articles.
    Placeholder for actual API integration (e.g., NewsAPI, Alpha Vantage).
    """
    def fetch_top_financial_news(self, query="financial market", count=3):
        # In a real scenario, this would call a news API like NewsAPI or Alpha Vantage
        # using os.getenv("NEWS_API_KEY") or similar for security.
        # For this example, returning mock data to ensure functionality without API keys.
        mock_articles = [
            {
                "title": "Market Sees Unexpected Dip Amidst Inflation Fears",
                "content": "Stocks tumbled today as new inflation data sparked concerns among investors. The Dow Jones Industrial Average fell by 2%, while tech stocks took a harder hit. Analysts are divided on whether this is a temporary correction or the start of a bear market. Energy prices continue to climb, adding to inflationary pressures."
            },
            {
                "title": "Tech Giant X Announces Record Q4 Earnings, Boosts Investor Confidence",
                "content": "Despite broader market concerns, Tech Giant X reported stellar earnings for the fourth quarter, exceeding analyst expectations. The company's innovative AI division was highlighted as a key growth driver. This news provided a much-needed boost to the tech sector, showing resilience in certain areas."
            },
            {
                "title": "Central Bank Hints at Further Rate Hikes to Combat Inflation",
                "content": "The Federal Reserve indicated it might need to implement more aggressive interest rate hikes than previously anticipated to bring inflation under control. This hawkish stance sent ripples through the bond market and led to further speculation about economic slowdowns in the coming months. Consumer spending data will be closely watched."
            },
            {
                "title": "Global Supply Chain Disruptions Continue to Impact Manufacturing",
                "content": "Ongoing challenges in global supply chains are severely affecting manufacturing output worldwide. Shortages of key components and increased shipping costs are leading to higher prices for consumers and reduced profit margins for businesses. Companies are exploring regionalization strategies to mitigate risks."
            }
        ]
        # Filter mock articles by query if present in title/content
        filtered_articles = [art for art in mock_articles if query.lower() in art['title'].lower() or query.lower() in art['content'].lower()]
        return filtered_articles[:count] if filtered_articles else mock_articles[:count]

class SentimentAnalyzer:
    """
    Analyzes the sentiment of text using a pre-trained LLM from Hugging Face.
    """
    def __init__(self):
        # Using a compact, pre-trained sentiment analysis model for efficiency
        self.nlp = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze_sentiment(self, text):
        """Returns sentiment (POSITIVE/NEGATIVE) and score."""
        # Truncate text for model input, as 'distilbert-base-uncased-finetuned-sst-2-english' has a max input of 512 tokens
        result = self.nlp(text[:512])
        return result[0]['label'], result[0]['score']

class RAGProcessor:
    """
    Retrieval-Augmented Generation for answering questions based on provided documents.
    This simplified RAG: Embeds documents, finds most similar, and synthesizes an answer.
    """
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.sentiment_analyzer = SentimentAnalyzer()

    def process_query(self, query, documents):
        """
        Processes a query against a list of document contents.
        Returns a concise answer and overall sentiment of the relevant info.
        """
        if not documents:
            return "No relevant documents provided for the query.", "NEUTRAL", 0.0

        document_contents = [doc['content'] for doc in documents]
        document_embeddings = self.model.encode(document_contents, convert_to_tensor=True)
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Find the most relevant document(s) using cosine similarity
        cosine_scores = util.cos_sim(query_embedding, document_embeddings)[0]
        top_k_indices = np.argsort(cosine_scores.cpu().numpy())[::-1][:2] # Get top 2 most relevant

        # Filter for documents above a relevance threshold
        relevant_docs_content = [
            document_contents[i] for i in top_k_indices if cosine_scores[i] > 0.4 # Adjustable threshold
        ]

        if not relevant_docs_content:
            return "No sufficiently relevant information found to answer the query from provided documents.", "NEUTRAL", 0.0

        # For a true RAG, the relevant_docs_content would be fed into a more powerful LLM (e.g., GPT-3.5/4 API)
        # to synthesize a nuanced answer. Here, we simulate a concise summary.
        context = " ".join(relevant_docs_content)
        
        # A simple LLM call simulation for summarization based on context and query
        # In a production system, this would be an actual API call to an LLM like OpenAI or Anthropic
        try:
            # Use the sentiment analyzer as a placeholder for LLM understanding to generate a basic answer
            # This is a simplification; a full LLM would generate text directly.
            summary_pipe = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
            generated_summary = summary_pipe(context, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
            answer_text = f"Based on relevant news: {generated_summary}. Regarding '{query}', the articles suggest..."
        except Exception:
            # Fallback if summarization model fails or is not available
            answer_text = f"Based on relevant news concerning '{query}': {context[:500]}... This suggests that factors mentioned in these articles are influencing the situation."


        # Analyze sentiment of the synthesized answer's underlying context
        overall_sentiment, sentiment_score = self.sentiment_analyzer.analyze_sentiment(context)

        return answer_text, overall_sentiment, sentiment_score

class FinIntelAgent:
    """
    Orchestrates financial intelligence gathering, sentiment analysis, and RAG.
    Acts as the main entry point for the agent's functionality.
    """
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.rag_processor = RAGProcessor()

    def run_daily_brief(self, market_query="financial market stability", deep_dive_query="impact of inflation on tech stocks"):
        """
        Executes the agent's daily briefing routine.
        Fetches news, analyzes sentiment, and provides RAG-powered deep dives.
        """
        print("\n--- FinIntel Agent Initiated ---")
        print(f"Fetching top news related to: '{market_query}'")
        articles = self.news_fetcher.fetch_top_financial_news(query=market_query, count=4)

        if not articles:
            print("No articles fetched for today's brief.")
            return None

        print("\n--- Analyzing News Sentiment ---")
        aggregated_sentiment_labels = []
        for i, article in enumerate(articles):
            label, score = self.sentiment_analyzer.analyze_sentiment(article['content'])
            print(f"Article {i+1}: '{article['title']}' - Sentiment: {label} (Score: {score:.2f})")
            aggregated_sentiment_labels.append(label)

        print(f"\n--- RAG-Powered Deep Dive: '{deep_dive_query}' ---")
        answer, overall_sentiment, sentiment_score = self.rag_processor.process_query(deep_dive_query, articles)
        print(f"Answer: {answer}")
        print(f"Overall Relevant Sentiment: {overall_sentiment} (Score: {sentiment_score:.2f})")

        # Example of a simple alert condition based on the deep dive
        if overall_sentiment == "NEGATIVE" and sentiment_score > 0.9:
            print("\n!!! URGENT ALERT: Strong negative sentiment detected for your deep-dive query. !!!")
        elif overall_sentiment == "POSITIVE" and sentiment_score > 0.9:
            print("\n### POSITIVE SIGNAL: Strong positive sentiment detected for your deep-dive query. ###")

        print("\n--- FinIntel Agent Briefing Complete ---")

        return {
            "articles": articles,
            "aggregated_sentiment_labels": aggregated_sentiment_labels,
            "rag_query": deep_dive_query,
            "rag_answer": answer,
            "rag_overall_sentiment": overall_sentiment,
            "rag_sentiment_score": sentiment_score
        }

if __name__ == "__main__":
    # Example usage:
    # Initialize the agent
    agent = FinIntelAgent()

    # Run the daily brief with a general market query and a specific deep-dive question
    briefing_results = agent.run_daily_brief(
        market_query="economy and interest rates",
        deep_dive_query="effect of recent inflation data on tech stock valuations"
    )

    if briefing_results:
        print("\nSummary of Briefing Results:")
        print(f"Total Articles Processed: {len(briefing_results['articles'])}")
        print(f"Aggregated Sentiments: {briefing_results['aggregated_sentiment_labels']}")
        print(f"Deep Dive Answer: {briefing_results['rag_answer'][:100]}...")
        print(f"Deep Dive Sentiment: {briefing_results['rag_overall_sentiment']} (Score: {briefing_results['rag_sentiment_score']:.2f})")
