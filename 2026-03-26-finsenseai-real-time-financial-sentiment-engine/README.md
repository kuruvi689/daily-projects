# FinSenseAI: Real-Time Financial Sentiment Engine

## Project Description

FinSenseAI is an AI-powered Python tool designed to monitor and analyze financial news sentiment in real-time. It automates the process of scraping financial articles from specified RSS feeds, extracting their core content, and then leveraging a Large Language Model (LLM) to perform sophisticated sentiment analysis. The insights, including sentiment scores, classifications (positive, negative, neutral), and summaries, are persistently stored in a local SQLite database for future analysis and tracking.

This tool aims to provide early signals and a structured view of market sentiment, helping users identify high-leverage opportunities and build robust financial wealth infrastructure.

## Motivation & Strategic Alignment

This project directly addresses two core pillars of the Teddy³ Strategic Goal Architecture:

1.  **Pillar 1: AI Mastery & Agentic Systems:** By integrating LLM orchestration for advanced text understanding and sentiment analysis, FinSenseAI sharpens mastery over "weapons" like RAG (in a broader sense of augmenting data with AI interpretation) and autonomous data processing agents.
2.  **Pillar 2: Financial Independence & Wealth Infrastructure:** FinSenseAI builds a crucial component of wealth infrastructure by providing actionable financial data analysis and market sentiment tracking. It represents an "engine" designed to inform strategic financial decisions, moving beyond conventional indicators towards AI-driven insights.

## Features

*   **Automated Article Scraping:** Fetches news articles from configurable RSS feeds, extracting titles, URLs, publication dates, and full content.
*   **Intelligent Text Extraction:** Cleans HTML content to extract the main body text of articles, focusing on relevant sections.
*   **LLM-Powered Sentiment Analysis:** Utilizes a Large Language Model (e.g., OpenAI's GPT models) to determine the sentiment (positive, negative, neutral) and a numerical score (-1.0 to 1.0) of financial news content.
*   **Concise Summarization:** The LLM also provides a brief summary (1-2 sentences) of the financial implications for each article.
*   **Persistent Data Storage:** Stores all scraped articles, their content, and the resulting sentiment analysis in a local SQLite database, including a unique URL constraint to prevent duplicates.
*   **Modularity:** Designed with distinct classes for scraping, LLM interaction, and database management, facilitating easy extension or component replacement.

## SaaS Potential

FinSenseAI has significant potential as a micro-service. Users would pay for:
*   **Curated Sentiment Feeds:** Access to real-time, AI-analyzed sentiment data for specific sectors, companies, or indices.
*   **API Access:** Developers could integrate FinSenseAI's API into their own trading bots, dashboards, or research tools.
*   **Custom Source Monitoring:** Allowing users to add their own private news sources or specialized feeds for sentiment tracking.
*   **Historical Data Access:** Providing access to a comprehensive historical database of financial sentiment trends and analysis.

A $5-$20/month subscription model for access to an API or a basic dashboard is highly viable, offering a clear value proposition for informed financial decision-making.

## Modularity Design

The project is structured into three main, independent classes, adhering to the principle of separation of concerns:

1.  **`ArticleScraper`**: Handles all web scraping logic, including fetching HTML content, parsing RSS feeds, and extracting clean text from articles. This component can be easily swapped for different scraping mechanisms (e.g., custom parsers for specific websites, API-based news services) without affecting the rest of the system.
2.  **`LLMSentimentAnalyzer`**: Encapsulates the logic for interacting with a Large Language Model to perform sentiment analysis. It can be adapted to use different LLM providers (e.g., Anthropic, local models via `ollama`) by modifying its internal `client` and prompt strategy, or by implementing an adapter pattern.
3.  **`SentimentDatabase`**: Manages the SQLite database, handling table creation, data insertion, and retrieval. This component can be extended to support different databases (e.g., PostgreSQL, MongoDB) with minimal impact on other parts of the system by simply changing the underlying database connector.

This modular design ensures that each core functionality can be developed, tested, and maintained independently, making the system robust, scalable, and easy to modify for future enhancements.

## Installation

1.  **Clone the repository:**
    bash
    git clone <repository_url_here>
    cd FinSenseAI
    

2.  **Create a virtual environment:**
    bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    

3.  **Install dependencies:**
    bash
    pip install -r requirements.txt
    

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your OpenAI API key:
    
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    
    (Ensure you have an OpenAI API key. For alternative LLMs, you would configure them accordingly.)

## Usage

To run the sentiment analysis engine:

bash
python finsense_ai.py


The script will perform the following steps:
1.  Scrape articles from the configured RSS feeds.
2.  Analyze the sentiment (and provide a summary) of each article using the LLM.
3.  Store the results in `finsense_data.db`.

You can inspect the `finsense_data.db` file using any SQLite browser (e.g., DB Browser for SQLite) to view the stored sentiment information and historical data.

## Configuration

*   **RSS Feeds:** Modify the `FINANCIAL_RSS_FEEDS` list in `finsense_ai.py` to add or remove financial news sources. You can find many free RSS feeds for financial news (e.g., Reuters, Yahoo Finance, etc.).
*   **LLM Model:** The `LLMSentimentAnalyzer` can be configured with a different `model` parameter during instantiation (e.g., `model="gpt-4"` for higher accuracy at a higher cost, or other models).
*   **Database Name:** The `SentimentDatabase` can be initialized with a different database file name if you wish to manage multiple databases.

## Future Enhancements

*   **Dashboard Integration:** Develop a simple web interface (e.g., Flask/Django) to visualize sentiment trends over time, providing a user-friendly way to interact with the data.
*   **Entity Extraction:** Enhance the LLM prompt to extract key entities (companies, stocks, sectors) from articles and track sentiment specifically for these entities.
*   **Alerting System:** Implement notifications (email, Slack, Telegram) for significant sentiment shifts, specific keywords, or when sentiment for a tracked entity crosses a predefined threshold.
*   **More Advanced Scraping:** Implement custom parsers for specific financial websites without robust RSS feeds, or integrate with premium news APIs for broader and more reliable data access.
*   **Benchmarking & Evaluation:** Develop a prompt evaluation framework to systematically test and compare LLM sentiment accuracy and cost-effectiveness across different models and prompts.
*   **Containerization:** Dockerize the entire application for easier deployment as a scalable microservice, simplifying dependency management and environment setup.
*   **Cloud Deployment:** Explore deployment options on cloud platforms (AWS, GCP, Azure) to run FinSenseAI as a persistent, always-on service.
