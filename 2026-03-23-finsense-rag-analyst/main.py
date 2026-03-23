import requests
import json
import os
import bs4
import feedparser
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# --- Configuration ---
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral") # Ensure mistral or similar is pulled: ollama run mistral
CHROMA_DB_PATH = "./chroma_db"
FINANCIAL_NEWS_SOURCES = [
    # Example RSS feeds - replace with actual relevant feeds
    "https://feeds.a.dj.com/rss/RssFeedDog.xml", # WSJ Top News
    "https://www.cnbc.com/id/100003114/device/rss/rss.html", # CNBC Investing
    # Add more URLs or RSS feeds as needed
]

# --- Helper Functions (Modular by design) ---

def fetch_rss_articles(url):
    """Fetches articles from an RSS feed and returns a list of dictionaries."""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            title = entry.title if hasattr(entry, 'title') else 'No Title'
            link = entry.link if hasattr(entry, 'link') else 'No Link'
            summary = entry.summary if hasattr(entry, 'summary') else 'No Summary'
            content = entry.content[0].value if hasattr(entry, 'content') and entry.content else summary
            articles.append({"title": title, "link": link, "content": content})
        return articles
    except Exception as e:
        print(f"Error fetching RSS from {url}: {e}")
        return []

def fetch_url_content(url):
    """Fetches and extracts main text content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        # Common tags for main content, adjust as needed for specific sites
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        text_content = ' '.join([p.get_text() for p in paragraphs])
        return text_content.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing content from {url}: {e}")
        return None

def chunk_text(text, chunk_size=500, overlap=50):
    """Splits text into smaller, overlapping chunks."""
    chunks = []
    if not text:
        return chunks
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

class CustomEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Custom embedding function using SentenceTransformers."""
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, texts):
        return self.model.encode(texts).tolist()

class RAGSystem:
    def __init__(self, db_path, embedding_model_name, ollama_api_base, ollama_model):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = CustomEmbeddingFunction(embedding_model_name)
        self.collection = self.client.get_or_create_collection(
            name="financial_news_collection",
            embedding_function=self.embedding_function
        )
        self.ollama_api_base = ollama_api_base
        self.ollama_model = ollama_model

    def add_documents(self, documents):
        """Adds documents (text chunks) to the ChromaDB collection."""
        if not documents:
            return
        ids = [f"doc_{i}" for i in range(self.collection.count(), self.collection.count() + len(documents))]
        self.collection.add(documents=documents, ids=ids)
        print(f"Added {len(documents)} documents to the collection.")

    def query_llm(self, prompt):
        """Sends a query to the local Ollama LLM and returns the response."""
        try:
            url = f"{self.ollama_api_base}/api/generate"
            headers = {"Content-Type": "application/json"}
            data = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False # We want the full response at once
            }
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No response from LLM.")
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Is it running at the specified API base?" 
                   "Please ensure `ollama serve` is running and the model is downloaded (e.g., `ollama run mistral`)."
        except requests.exceptions.RequestException as e:
            return f"Error querying Ollama LLM: {e}"

    def retrieve_and_generate(self, query, n_results=5):
        """Performs RAG: retrieves relevant documents and uses LLM to generate an answer."""
        if self.collection.count() == 0:
            return "The knowledge base is empty. Please ingest some financial news first."

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents']
        )
        retrieved_docs = results['documents'][0] if results['documents'] else []

        if not retrieved_docs:
            return "No relevant information found in the knowledge base for your query."

        context = "\n\n".join(retrieved_docs)
        prompt = f"""Based on the following financial news context, answer the user's query.
        
        Context:
        {context}
        
        Query: {query}
        
        Provide a concise summary, key sentiment (positive, negative, neutral), and any actionable insights related to investments. If the information is not sufficient, state that clearly.
        """
        
        print("\n--- Sending query to LLM ---")
        llm_response = self.query_llm(prompt)
        print("--- LLM Response Received ---")
        return llm_response

# --- Main Application Logic ---

def main():
    print("Initializing FinSense RAG Analyst...")
    rag_system = RAGSystem(
        db_path=CHROMA_DB_PATH,
        embedding_model_name="all-MiniLM-L6-v2",
        ollama_api_base=OLLAMA_API_BASE,
        ollama_model=OLLAMA_MODEL
    )

    # Step 1: Ingest financial news (can be done periodically)
    print("\nFetching and processing financial news...")
    all_chunks = []
    for source_url in FINANCIAL_NEWS_SOURCES:
        if "rss" in source_url:
            articles = fetch_rss_articles(source_url)
            for article in articles:
                if article['content']:
                    chunks = chunk_text(article['content'])
                    all_chunks.extend(chunks)
        else:
            content = fetch_url_content(source_url)
            if content:
                chunks = chunk_text(content)
                all_chunks.extend(chunks)

    if all_chunks:
        rag_system.add_documents(all_chunks)
    else:
        print("No news articles fetched or processed from configured sources.")
        print("Adding dummy content for demonstration purposes if no real data is available...")
        dummy_content = [
            "Tesla stock shows strong performance after Q4 earnings, surprising analysts with increased EV deliveries.",
            "Analysts are cautious about the upcoming inflation report, suggesting potential market volatility.",
            "Google invests heavily in AI research, signaling long-term growth in the technology sector.",
            "Oil prices surged today due to geopolitical tensions in the Middle East, impacting energy stocks.",
            "Major banks reported higher than expected profits due to rising interest rates, leading to positive market reactions."
        ]
        rag_system.add_documents(dummy_content)


    # Step 2: Allow user to query the system
    print("\nFinSense RAG Analyst is ready. Ask your financial questions!")
    print(f"Using Ollama model: {OLLAMA_MODEL} at {OLLAMA_API_BASE}")
    print("Ensure Ollama is running and the model is downloaded (e.g., 'ollama run mistral').")
    while True:
        user_query = input("\nEnter your financial query (or 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break
        
        response = rag_system.retrieve_and_generate(user_query)
        print("\n--- FinSense RAG Analyst Response ---")
        print(response)
        print("-----------------------------------")

if __name__ == "__main__":
    main()