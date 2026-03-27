# FinSenseScout: AI Financial News Sentiment Scraper

## Project Overview
FinSenseScout is a modular Python application designed to autonomously scrape financial news articles from the web and perform sentiment analysis on their content using an AI-driven approach. This tool serves as a foundational component for understanding real-time market sentiment, providing a critical edge for financial decision-making and wealth infrastructure development.

While the current implementation uses a mock LLM for sentiment analysis to minimize external dependencies for demonstration, its architecture is built for seamless integration with real Large Language Models (LLMs) like OpenAI's GPT series, Hugging Face models, or custom fine-tuned models.

## Strategic Alignment: TeddyÂ³ Goals

This project directly contributes to multiple strategic pillars of TeddyÂ³'s Goal Architecture:

1.  **AI Mastery & Agentic Systems (Pillar 1)**
    *   **Focus:** Demonstrates LLM orchestration (via the `MockLLMSentiment` class, designed for real LLM integration) and autonomous task execution (the web scraping agent). 
    *   **Strategic Outcome:** Mastering the "weapons" of the 2026 economy by building a system that can autonomously gather and interpret complex, unstructured data, a core capability for future AI agents.

2.  **Financial Independence & Wealth Infrastructure (Pillar 2)**
    *   **Focus:** Provides a robust mechanism for financial data analysis (market sentiment). Understanding sentiment from news can inform investment strategies, arbitrage opportunities, and risk management.
    *   **Strategic Outcome:** Building the "engine" that replaces the salary bribe by automating the continuous analysis of market-moving information, enabling data-driven financial decisions without manual effort.

3.  **Strategic Thinking & Decision Frameworks (Pillar 4)**
    *   **Focus:** By delivering actionable sentiment data, this tool contributes to a logical modeling framework. It provides a data point to weigh against other financial indicators, enhancing the overall decision-making process.
    *   **Strategic Outcome:** Sharpening the "mind" to identify high-leverage opportunities before others by giving early insights into shifts in market mood, which often precedes price movements.

## Key Features

*   **Modular Web Scraper:** The `FinancialNewsScraper` class is designed for extensibility, capable of fetching content from various news sources.
*   **AI-Driven Sentiment Analysis:** Employs (or mocks the use of) an LLM for nuanced sentiment extraction from article text.
*   **Structured Output:** Presents analyzed news with title, URL, detected sentiment, a confidence score, and a content preview.
*   **Error Handling:** Includes basic error handling for HTTP requests during scraping.
*   **SaaS Potential:** Designed with micro-service potential, offering real-time financial sentiment feeds for subscribers.

## SaaS Potential

FinSenseScout is engineered with clear SaaS potential. A refined version could be offered as a micro-service, allowing users to:

*   **Subscribe to Custom Feeds:** Users could define their list of financial news sources and receive sentiment analysis reports.
*   **API Access:** Provide an API endpoint for other applications to query sentiment for specific URLs or receive aggregated daily/hourly sentiment scores across various sectors.
*   **Alerting System:** Integrate with an alerting system (email, SMS, push notifications) for significant sentiment shifts in monitored assets or markets.

Customers would pay a recurring fee (e.g., $5-$50/month) for curated, AI-driven financial intelligence, saving time on manual news consumption and analysis.

## Modularity

The project adheres to modularity principles:

*   **`FinancialNewsScraper`:** Handles all web scraping logic, independent of sentiment analysis.
*   **`MockLLMSentiment`:** Encapsulates the (mocked) LLM interaction, allowing easy replacement with a real LLM API client without affecting other parts.
*   **`FinSenseScout` (Orchestrator):** Coordinates the scraper and analyzer, providing a clean interface for overall functionality.

This modular design ensures that components can be reused in larger systems or easily updated/replaced as technology evolves.

## Usage

### Prerequisites

Ensure you have Python 3.9+ installed.

### Installation

1.  Save the provided code as `finsensescout.py`.
2.  Install the necessary Python packages:
    bash
    pip install -r requirements.txt
    

### Running the Application

Execute the script from your terminal:

bash
python finsensescout.py


The script will attempt to scrape articles from predefined example URLs and then apply sentiment analysis. It includes mock articles for demonstration if live scraping encounters issues.

### Configuration

*   **`example_news_urls`**: Modify the `example_news_urls` list in the `if __name__ == "__main__":` block to target different financial news sources.
*   **LLM Integration**: To integrate a real LLM, modify the `MockLLMSentiment` class to use an actual API (e.g., `openai.ChatCompletion.create`, `transformers` pipelines) and potentially load an API key from environment variables.

## Project Structure


finsensescout.py
requirements.txt


*   `finsensescout.py`: Contains the `MockLLMSentiment`, `FinancialNewsScraper`, and `FinSenseScout` classes, along with the main execution logic.
*   `requirements.txt`: Lists all Python dependencies.

## Future Enhancements

*   **Real LLM Integration:** Replace `MockLLMSentiment` with a client for a production-grade LLM (e.g., OpenAI, Anthropic, local open-source models).
*   **Robust Scraping:** Implement more advanced scraping techniques (e.g., headless browsers for JavaScript-heavy sites, rotating proxies, handling CAPTCHAs, custom parsers for specific news sites).
*   **Data Persistence:** Integrate with a database (SQL, NoSQL) to store historical sentiment data for trend analysis.
*   **Sentiment Aggregation:** Add functionality to aggregate sentiment across multiple articles for a specific stock, sector, or the broader market.
*   **User Interface:** Develop a simple web UI (e.g., Flask/Streamlit) to display results and allow custom input.
*   **Alerting:** Implement notifications for significant sentiment shifts.
*   **Entity Recognition:** Use LLMs to identify key entities (companies, people, products) within articles and associate sentiment with them.
