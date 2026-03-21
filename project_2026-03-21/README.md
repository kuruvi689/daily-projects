# FinSenseAI: Automated Financial News Sentiment Aggregator

## Project Goal
FinSenseAI is a Python-based tool designed to automatically fetch financial news and analyze its sentiment using large language models (LLMs). This project aims to provide actionable insights into market sentiment, helping users identify potential financial trends and build robust wealth infrastructure.

## Strategic Alignment (TeddyÂ³ Pillars)

This project directly addresses two core pillars of the TeddyÂ³ Strategic Goal Architecture:

1.  **AI Mastery & Agentic Systems (Pillar 1 - "weapons of the 2026 economy"):**
    *   **LLM Orchestration:** Integrates advanced LLMs for sophisticated natural language processing, specifically for sentiment analysis of complex financial texts.
    *   **Autonomous Task Execution:** Automates the end-to-end process of news retrieval, analysis, and aggregation, laying groundwork for more complex agentic systems.

2.  **Financial Independence & Wealth Infrastructure (Pillar 2 - "engine that replaces the salary bribe"):**
    *   **Financial Data Analysis:** Provides critical, AI-driven sentiment data derived from financial news, enhancing understanding of market dynamics.
    *   **Algorithmic Calculation:** Generates quantifiable sentiment scores and aggregates them, which can feed directly into algorithmic trading strategies or portfolio adjustment decisions.

## Features

*   **Mock Financial News Fetcher:** Simulates the retrieval of diverse financial news articles (easily extendable to real RSS feeds, APIs, or custom web scraping).
*   **LLM-Powered Sentiment Analysis:** Utilizes a specified LLM (e.g., OpenAI's GPT models) to deeply understand and score the sentiment of each article for its financial implications.
*   **Sentiment Aggregation:** Compiles individual article sentiments into an overall market summary, including average scores and sentiment distribution.
*   **Structured Output:** Stores detailed individual analysis and aggregated summaries in a JSON file for further processing or visualization.
*   **Modular Design:** Code is structured into logical components (scraper, analyzer, aggregator) for easy extension, maintenance, and reuse.

## Technical Constraints Adherence

*   **No Tutorials:** This is a specialized, high-leverage tool focused on generating strategic financial insights, far beyond a generic "calculator" or "to-do list."
*   **SaaS Potential:** The core sentiment analysis engine, especially if connected to real-time news streams and entity recognition, could be offered as a micro-service. Users (e.g., retail investors, small funds) could pay a monthly subscription ($5-$20/month) for curated sentiment feeds on specific stocks, sectors, or market indices.
*   **Modularity:** The `fetch_financial_news_mock` (scraper), `analyze_sentiment_with_llm` (LLM interaction/analyzer), and `aggregate_sentiment_results` (aggregator) functions are distinct and can be easily refactored into separate modules or microservices. The LLM interaction is abstracted, allowing different LLM providers to be plugged in.
*   **Self-Documentation:** This `README.md` provides a comprehensive overview of the project's purpose, functionality, and strategic value.

## Setup and Installation

1.  **Save the code:** Save the provided Python code as `fin_sense_ai.py` (or `main.py`).

2.  **Create a virtual environment (recommended):**
    bash
    python -m venv .venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    

3.  **Install dependencies:**
    bash
    pip install requests
    
    (Note: `json` and `os` are standard Python libraries and do not require installation).

4.  **Set up OpenAI API Key:**
    Obtain an API key from [OpenAI](https://platform.openai.com/account/api-keys).
    Set it as an environment variable before running the script:
    bash
    export OPENAI_API_KEY="your_openai_api_key_here"
    # On Windows (in Command Prompt): set OPENAI_API_KEY="your_openai_api_key_here"
    # On Windows (in PowerShell): $env:OPENAI_API_KEY="your_openai_api_key_here"
    
    **Important:** Never hardcode API keys directly into your scripts or commit them to version control.

## Usage

Run the script from your terminal:

bash
python fin_sense_ai.py


The script will:
1.  Fetch mock financial news articles.
2.  Send each article's content to the OpenAI LLM for sentiment analysis.
3.  Print individual article sentiments and an overall market summary to the console.
4.  Save the detailed results to `fin_sense_ai_results.json` in the current directory.

## Example Output (Console Snippet)


[FinSenseAI] Starting financial news sentiment analysis...
[__main__] Fetched 4 mock financial news articles.
[FinSenseAI] Analyzing sentiment for: 'Tech Giant X Reports Record Q3 Earnings, Shares Soar'...
[FinSenseAI] Analyzing sentiment for: 'Global Supply Chain Disruptions Continue to Hit Manufacturing Sector'...
[FinSenseAI] Analyzing sentiment for: 'New Interest Rate Hike Expected as Inflation Concerns Mount'...
[FinSenseAI] Analyzing sentiment for: 'Biotech Startup Y Secures Major Funding Round for Cancer Research'...

--- Individual Article Analysis ---
Title: Tech Giant X Reports Record Q3 Earnings, Shares Soar
  Sentiment: positive (Score: 0.95)
  Reason: The article highlights record earnings, strong growth in key divisions, and successful product launches, all highly positive indicators for the company's financial performance and stock valuation.

Title: Global Supply Chain Disruptions Continue to Hit Manufacturing Sector
  Sentiment: negative (Score: -0.70)
  Reason: The text explicitly mentions "persistent supply chain issues," "production delays," and "increased costs," which are all negative factors for the manufacturing sector's profitability.

Title: New Interest Rate Hike Expected as Inflation Concerns Mount
  Sentiment: negative (Score: -0.60)
  Reason: An interest rate hike is generally seen as negative for economic growth and consumer spending, which can impact corporate earnings and stock market performance. Inflation concerns further contribute to a pessimistic outlook.

Title: Biotech Startup Y Secures Major Funding Round for Cancer Research
  Sentiment: positive (Score: 0.85)
  Reason: Securing a significant funding round is a strong positive signal for a startup, indicating investor confidence and providing capital for accelerated research and development, potentially leading to future breakthroughs and profitability.

--- Overall Market Sentiment Summary ---
{
    "overall_sentiment": "mixed/neutral",
    "average_score": 0.125,
    "sentiment_distribution": {
        "positive": 2,
        "negative": 2,
        "neutral": 0,
        "error": 0
    },
    "total_articles": 4
}

[FinSenseAI] Results saved to fin_sense_ai_results.json


## Future Enhancements

*   **Real-time News Integration:** Connect to actual financial news APIs (e.g., NewsAPI, Alpha Vantage) or robust RSS feeds for live data.
*   **Entity Recognition:** Integrate Named Entity Recognition (NER) to identify specific companies, stocks, or sectors mentioned in the news and perform sentiment analysis at that granular level.
*   **Time-Series Analysis:** Store historical sentiment data in a database (e.g., PostgreSQL, MongoDB) to track trends and correlate with market movements.
*   **Dashboard & Visualization:** Develop a simple web interface (e.g., using Flask/Streamlit) to display sentiment trends and key insights.
*   **Alerting System:** Implement custom alerts for significant shifts in sentiment for particular assets.
*   **Multi-LLM Support:** Abstract the LLM client further to easily switch between different models or providers (e.g., Hugging Face models, Gemini).
*   **Configurability:** Externalize news sources, LLM parameters, and aggregation rules into a configuration file.
