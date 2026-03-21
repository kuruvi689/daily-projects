# FinSenseAI: News Sentiment Scorer

## Project Overview

FinSenseAI is a Python tool designed to analyze real-time market sentiment for specific stock tickers or companies by processing recent financial news headlines. It leverages a pre-trained financial-specific Transformer model (FinBERT) to classify headline sentiment and generate a composite sentiment score, providing a quick pulse on market perception.

This project is built to move the needle on key strategic pillars for Teddy³:

*   **Pillar 1: AI Mastery & Agentic Systems**: Focuses on advanced NLP (Natural Language Processing) through Transformer models for real-time sentiment analysis, a core component for future agentic systems in finance.
*   **Pillar 2: Financial Independence & Wealth Infrastructure**: Provides actionable insights into market sentiment, a critical input for algorithmic trading strategies, portfolio management, and investment decision-making. It aims to build tools that inform wealth-building activities.
*   **Pillar 3: Technical Architectural Skills**: Demonstrates the implementation of robust, modular code, efficient use of local machine learning models (with GPU acceleration if available), and best practices for API integration and error handling, contributing to a "fortress" of autonomous systems.

## Strategic Outcome

By mastering AI-driven market analysis, FinSenseAI contributes to:
*   **Mastering the "weapons" of the 2026 economy**: Sentiment analysis is a key component for automated trading, risk assessment, and strategic market positioning.
*   **Building the "engine" that replaces the salary bribe**: Providing independent, AI-driven financial insights reduces reliance on traditional, slow information channels and can power independent wealth generation.
*   **Building a "fortress" that functions with 100% autonomy**: Utilizing local models minimizes external dependencies and enhances system robustness and control.

## Features

*   **Ticker-Based News Fetching**: Retrieves relevant news headlines using the NewsAPI.org.
*   **Financial Sentiment Analysis**: Employs the `ProsusAI/finbert` Transformer model for accurate, finance-specific sentiment classification (Positive, Negative, Neutral).
*   **Composite Sentiment Scoring**: Calculates an aggregate sentiment score (between -1 and 1) representing the overall market mood for the queried entity.
*   **Detailed Insights**: Presents counts of positive, negative, and neutral headlines, along with a list of key headlines and their individual sentiment.
*   **Modular Design**: Structured into distinct functions and a class for easy integration into larger systems or microservices.

## SaaS Potential & Modularity

This tool is designed with micro-service potential in mind. The `NewsSentimentAnalyzer` class can be easily wrapped into a FastAPI endpoint, allowing it to serve sentiment data on demand. Individual components like `fetch_news_headlines` or `analyze_headlines_sentiment` can be reused in other financial data analysis or AI agent projects. Imagine a service providing daily sentiment reports for a personalized watch list for a monthly subscription.

## Installation

1.  **Clone the repository (or save the code):**
    (Or just save the provided Python code as `finsense_ai.py`)

2.  **Create a virtual environment (recommended):**
    bash
    python -m venv venv
    source venv/bin/activate # On Windows: .\venv\Scripts\activate
    

3.  **Install dependencies:**
    bash
    pip install -r requirements.txt
    
    The `requirements.txt` should contain:
    
    transformers
    requests
    torch # Required by transformers for model execution
    

## Configuration

**NewsAPI Key**:
You need a free API key from [NewsAPI.org](https://newsapi.org/). Once obtained, set it as an environment variable:

bash
export NEWS_API_KEY='YOUR_NEWSAPI_KEY_HERE'

(On Windows Command Prompt: `set NEWS_API_KEY=YOUR_NEWSAPI_KEY_HERE`)
(On Windows PowerShell: `$env:NEWS_API_KEY='YOUR_NEWSAPI_KEY_HERE'`)

## Usage

Run the script from your terminal:

bash
python finsense_ai.py


The script will prompt you to enter a stock ticker or company name (e.g., `TSLA`, `Apple`, `NVIDIA`). It will then fetch news, analyze sentiment, and display a summary report.

**Example Output (conceptual):**


Fetching news for: TSLA...
Analyzing sentiment of 10 headlines...

--- FinSenseAI Market Sentiment Report ---
Query: TSLA
Total Headlines Analyzed: 10
Positive: 3 | Negative: 2 | Neutral: 5
Composite Sentiment Score (range -1 to 1): 0.1500

Top Sentiment Headlines:

Strongest Positive:
  [POSITIVE 0.98] Tesla Stock Surges on Record Deliveries
  [POSITIVE 0.95] Analysts Upgrade Tesla Rating Ahead of Earnings

Strongest Negative:
  [NEGATIVE 0.92] Tesla Faces New Regulatory Scrutiny
  [NEGATIVE 0.88] Supply Chain Issues Could Impact Tesla Production

Note: Score near 1 is strongly positive, near -1 is strongly negative.
       FinBERT model typically outputs 'positive', 'negative', 'neutral' labels.


## Future Enhancements

*   **RAG Integration**: Implement Retrieval-Augmented Generation to fetch and analyze specific documents (e.g., earnings call transcripts, SEC filings) alongside general news.
*   **Social Media Analysis**: Extend data acquisition to include platforms like Twitter/X or Reddit for a broader sentiment picture.
*   **Time-Series Analysis**: Track sentiment over time to identify trends and shifts.
*   **Alerting System**: Integrate with messaging platforms (e.g., Slack, Email) to send alerts when sentiment crosses certain thresholds.
*   **User Interface**: Develop a simple web interface (e.g., using Flask/FastAPI and React) to visualize sentiment trends.
*   **Multiple Models**: Allow switching between different financial sentiment models or ensemble approaches.