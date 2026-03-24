import os
import datetime
from collections import deque

class MockLLM:
    """
    A mock LLM to simulate text generation for synthesis.
    In a real application, this would integrate with actual LLM APIs (e.g., OpenAI, Anthropic).
    """
    def generate(self, prompt, context=""):
        if "market sentiment" in prompt.lower():
            if "positive" in context.lower() or "growth" in context.lower() or "jumps" in context.lower() or "raises" in context.lower() or "acquires" in context.lower() or "stabilize" in context.lower():
                return "The market sentiment appears cautiously optimistic due to recent positive earnings, funding rounds, strategic acquisitions, and stabilizing commodity prices."
            elif "negative" in context.lower() or "decline" in context.lower() or "loss" in context.lower() or "concerns rise" in context.lower():
                return "A bearish sentiment is noted, driven by inflation concerns, interest rate hikes, and reported banking sector losses."
            else:
                return "Market sentiment is mixed, awaiting further economic indicators."
        elif "investment opportunity" in prompt.lower() or "high-leverage" in prompt.lower():
            if "acquire" in context.lower() or "partnership" in context.lower() or "disruptor" in context.lower() or "expansion" in context.lower() or "funding" in context.lower() or "groundbreaking research" in context.lower():
                return "Potential acquisition targets identified in the tech and pharma sectors, showing strong synergy. An emerging FinTech disruptor has also secured significant funding for expansion."
            else:
                return "No immediate high-leverage investment opportunities detected based on the provided data."
        return f"Synthesized insight: {context[:200].strip()}... (Query: {prompt[:100].strip()})"

class NewsFetcher:
    """
    Modular component to fetch financial news articles.
    In a real system, this would integrate with RSS feeds, news APIs (e.g., NewsAPI, Financial Times API).
    """
    def __init__(self, sources=None):
        self.sources = sources if sources else ["Mock Finance News", "Mock Tech News"]
        self.mock_articles = deque([
            {"title": "Tech Company X Announces Record Q4 Earnings, Stock Jumps 10%", "content": "Company X reported significant growth, beating analyst expectations. Acquisition rumors are circulating. This indicates a strong market position.", "date": "2026-03-23"},
            {"title": "Global Inflation Concerns Rise Amidst Energy Price Volatility", "content": "Economists warn of persistent inflation pressures, potentially leading to further interest rate hikes. This could impact consumer spending and corporate profits.", "date": "2026-03-23"},
            {"title": "FinTech Startup Y Raises $50M Series B, Eyes Expansion", "content": "Startup Y secured substantial funding, planning to expand into new markets. This could be a disruptor in the financial services sector. Potential for partnership or investment.", "date": "2026-03-24"},
            {"title": "Major Bank Z Reports Quarterly Loss, Cites Bad Loans", "content": "Bank Z's poor performance has raised concerns about the stability of the banking sector. Regulatory scrutiny is expected. This could signal broader economic issues.", "date": "2026-03-24"},
            {"title": "Commodity Prices Stabilize After Recent Surge, Easing Inflation Fears", "content": "After weeks of volatility, key commodity prices show signs of stabilization. This might ease inflationary pressures and support economic recovery.", "date": "2026-03-24"},
            {"title": "Pharma Giant A Acquires Biotech Innovator B for $1.2B", "content": "Pharma Giant A strengthens its pipeline with the acquisition of Biotech Innovator B, known for its groundbreaking research. This strategic move is expected to drive future revenue growth.", "date": "2026-03-24"}
        ])

    def fetch_recent_articles(self, limit=3):
        """Simulates fetching the most recent articles. Pops from the deque to simulate new data streams."""
        articles = []
        for _ in range(min(limit, len(self.mock_articles))):
            articles.append(self.mock_articles.popleft()) 
        return articles

class RAGSynthesizer:
    """
    Modular component for Retrieval-Augmented Generation (RAG).
    In a real system, this would involve embedding, vector DB, and an actual LLM orchestrated by a framework like LangChain or LlamaIndex.
    """
    def __init__(self, llm_model):
        self.llm = llm_model
        # self.knowledge_base = [] # In a real RAG, this would be a vector DB index

    def retrieve_and_synthesize(self, query, articles):
        """
        Simulates retrieving relevant info and synthesizing with an LLM.
        For this mock, it simply passes all article content as context to the LLM.
        In a real RAG, a retrieval step would select only the most relevant chunks.
        """
        full_context = "\n".join([f"Title: {a['title']}. Content: {a['content']}" for a in articles])
        prompt = f"Given the following financial news, provide a concise summary, identify key market sentiment, and highlight any potential high-leverage investment opportunities: {query}"
        return self.llm.generate(prompt, context=full_context)

class OpportunityNotifier:
    """
    Modular component to evaluate synthesized insights and trigger actionable notifications.
    """
    def __init__(self, sensitivity=0.7): # Sensitivity could filter minor vs. major opportunities
        self.sensitivity = sensitivity 

    def evaluate_and_notify(self, synthesized_insight):
        """
        Evaluates the insight for specific keywords indicating opportunities or critical alerts.
        Returns a notification string if an opportunity or critical alert is found.
        """
        notification = "No high-leverage opportunities or critical alerts requiring immediate action identified."
        insight_lower = synthesized_insight.lower()

        if "potential acquisition target" in insight_lower or "investment opportunity" in insight_lower or "strong synergy" in insight_lower or "groundbreaking research" in insight_lower or "strategic move" in insight_lower:
            notification = f"ACTION REQUIRED: High-leverage investment opportunity detected: {synthesized_insight}"
        elif "disruptor" in insight_lower and "expansion" in insight_lower and "funding" in insight_lower:
             notification = f"ALERT: Emerging market disruptor identified with significant funding: {synthesized_insight}"
        elif "stock jumps" in insight_lower and "record earnings" in insight_lower:
            notification = f"MARKET ALERT: Significant positive news for an asset; analyze further: {synthesized_insight}"
        elif "bearish sentiment" in insight_lower or "quarterly loss" in insight_lower or "concerns rise" in insight_lower:
            notification = f"CAUTION: Negative market indicator detected; assess risk: {synthesized_insight}"

        return notification

class FinInsightAI:
    """
    Orchestrates the entire FinInsight AI agent: news fetching, RAG synthesis, and opportunity notification.
    Designed for modularity, scalability, and SaaS readiness as a microservice.
    """
    def __init__(self, news_fetcher, rag_synthesizer, opportunity_notifier):
        self.news_fetcher = news_fetcher
        self.rag_synthesizer = rag_synthesizer
        self.opportunity_notifier = opportunity_notifier
        self.log_file = "fininsight_ai_log.txt"
        # Ensure log file exists
        if not os.path.exists(self.log_file):
            open(self.log_file, 'a').close()

    def _log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}") # Also print to console for immediate feedback

    def run_cycle(self, query="What are the latest market insights and high-leverage investment opportunities?"):
        """
        Executes a full cycle: fetch news, synthesize with RAG, evaluate for opportunities, and generate a notification/summary.
        """
        self._log("Starting FinInsight AI cycle...")

        # 1. Fetch recent articles
        articles = self.news_fetcher.fetch_recent_articles()
        if not articles:
            self._log("No new articles fetched. Skipping synthesis.")
            return {
                "status": "no_new_articles",
                "summary": "No new articles available to process.",
                "opportunities": "No new opportunities detected.",
                "processed_articles_count": 0,
                "timestamp": datetime.datetime.now().isoformat()
            }

        self._log(f"Fetched {len(articles)} articles.")
        # self._log(f"Articles: {[a['title'] for a in articles]}") # Uncomment for debugging article titles

        # 2. Synthesize using RAG
        synthesized_insight = self.rag_synthesizer.retrieve_and_synthesize(query, articles)
        self._log(f"Synthesized Insight: {synthesized_insight}")

        # 3. Evaluate for opportunities and notify
        opportunity_alert = self.opportunity_notifier.evaluate_and_notify(synthesized_insight)
        self._log(f"Opportunity Alert: {opportunity_alert}")

        self._log("FinInsight AI cycle complete.")

        return {
            "status": "success",
            "summary": synthesized_insight,
            "opportunities": opportunity_alert,
            "processed_articles_count": len(articles),
            "timestamp": datetime.datetime.now().isoformat()
        }

# Example of how the agent could be instantiated and run
if __name__ == "__main__":
    print("\n--- Initializing FinInsight AI for a demonstration run ---")
    llm = MockLLM()
    news_fetcher = NewsFetcher()
    rag_synthesizer = RAGSynthesizer(llm)
    opportunity_notifier = OpportunityNotifier()

    fininsight_agent = FinInsightAI(news_fetcher, rag_synthesizer, opportunity_notifier)
    
    # Run a cycle and capture the output
    result = fininsight_agent.run_cycle()
    
    print("\n--- Agent's Final Output (Demonstration) ---")
    import json
    print(json.dumps(result, indent=2))

    # To demonstrate subsequent runs picking up new 'news'
    print("\n--- Running FinInsight AI for a second cycle to simulate new data ---")
    result_2 = fininsight_agent.run_cycle("Identify any new market shifts or critical risks.")
    print(json.dumps(result_2, indent=2))
