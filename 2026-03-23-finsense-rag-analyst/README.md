# FinSense RAG Analyst

## Project Goal
The FinSense RAG Analyst is a strategic Python tool designed to enhance financial intelligence by leveraging Retrieval-Augmented Generation (RAG) on financial news. It aims to provide concise summaries, sentiment analysis, and actionable insights from a continuously updated knowledge base of financial articles. This project contributes significantly to the "AI Mastery & Agentic Systems" and "Financial Independence & Wealth Infrastructure" pillars of Teddy³'s strategic goal architecture.

## Strategic Alignment
*   **Pillar 1: AI Mastery & Agentic Systems**
    *   **Focus**: LLM orchestration, RAG, and autonomous task execution.
    *   **Contribution**: Implements a RAG system for intelligent information retrieval and synthesis, showcasing mastery in deploying AI for specific, high-value tasks.
    *   **Strategic Outcome**: Mastering the "weapons" of the 2026 economy by building a system capable of real-time financial intelligence.
*   **Pillar 2: Financial Independence & Wealth Infrastructure**
    *   **Focus**: Financial data analysis and market sentiment.
    *   **Contribution**: Provides AI-driven insights into market trends and company-specific news, directly aiding in informed investment decisions.
    *   **Strategic Outcome**: Building the "engine" that replaces the salary bribe by automating key aspects of financial research and analysis.

## SaaS Potential & Modularity
This tool is designed with SaaS potential in mind. It could be offered as a micro-service where users subscribe to receive daily market briefings tailored to their portfolios, or pay-per-query for deep dives into specific companies or sectors. Its modular design (news fetching, text processing, vector database management, RAG engine, LLM interaction) ensures that components can be easily extended, swapped, or integrated into larger, more complex financial analysis platforms.

## Technical Implementation Highlights
*   **News Ingestion**: Fetches financial news from specified RSS feeds and URLs (configurable in `FINANCIAL_NEWS_SOURCES`).
*   **Text Processing**: Cleans and chunks raw text content for efficient storage and retrieval.
*   **Vector Database**: Utilizes `ChromaDB` as a persistent vector store to manage document embeddings.
*   **Embedding Model**: Employs `sentence-transformers` (specifically `all-MiniLM-L6-v2`) for generating high-quality text embeddings locally.
*   **Retrieval-Augmented Generation (RAG)**: Integrates a local Large Language Model (LLM) via `Ollama` (defaulting to `mistral`) to synthesize answers based on retrieved context, providing coherent and contextually relevant financial insights.
*   **Sentiment & Insight Extraction**: Prompts the LLM to identify sentiment and actionable investment insights from the synthesized information.

## How to Run

### Prerequisites
1.  **Python 3.8+**: Ensure you have Python installed.
2.  **Ollama**: Install [Ollama](https://ollama.ai/) and pull the `mistral` model (or your preferred model) by running `ollama run mistral` in your terminal. Ensure the Ollama server is running (usually `ollama serve` or it starts automatically).
3.  **Dependencies**: Install the required Python packages by creating a `requirements.txt` file (see 'requirements' section below) and running:
    bash
    pip install -r requirements.txt
    

### Setup & Execution
1.  **Save the file**: Save the provided Python code as `fin_sense_rag_analyst.py` in your desired project directory.
2.  **Environment Variables (Optional but Recommended)**:
    You can configure the Ollama API base URL and model via environment variables:
    bash
    export OLLAMA_API_BASE="http://localhost:11434" # Default
    export OLLAMA_MODEL="mistral"                  # Default
    
3.  **Run the application**:
    bash
    python fin_sense_rag_analyst.py
    
    The application will first attempt to ingest news, then prompt you for financial queries.

### Example Interaction

Initializing FinSense RAG Analyst...

Fetching and processing financial news...
Added X documents to the collection. # (or 'Adding dummy content...')

FinSense RAG Analyst is ready. Ask your financial questions!
Using Ollama model: mistral at http://localhost:11434
Ensure Ollama is running and the model is downloaded (e.g., 'ollama run mistral').

Enter your financial query (or 'exit' to quit): What is the sentiment around Tesla stock after its recent earnings report?

--- Sending query to LLM ---
--- LLM Response Received ---

--- FinSense RAG Analyst Response ---
Based on the context, Tesla's stock performance appears strong following its Q4 earnings report, with increased EV deliveries surprising analysts.
Key sentiment: Positive.
Actionable insights: This might indicate a good entry point or hold for investors interested in the EV sector, especially if the delivery growth trend continues. However, always conduct further due diligence.
-----------------------------------

Enter your financial query (or 'exit' to quit): exit


## Future Enhancements
*   **Dynamic News Source Management**: Allow users to add/remove RSS feeds and URLs through a configuration file or simple API.
*   **Scheduled Ingestion**: Implement scheduled tasks (e.g., using `APScheduler` or a cron job) for automatic daily/hourly news fetching.
*   **Advanced Sentiment Analysis**: Integrate dedicated financial sentiment analysis models for more nuanced and specialized sentiment scoring.
*   **Portfolio Integration**: Link insights directly to a user's specific portfolio holdings for personalized impact analysis.
*   **User Interface**: Develop a web-based UI (e.g., with Flask/FastAPI and a frontend framework) for easier interaction and visualization of insights.
*   **Cloud Deployment**: Containerize (Docker) for easier deployment on cloud platforms as a scalable micro-service.