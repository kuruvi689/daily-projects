import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class DocumentProcessor:
    """
    Handles loading, splitting, and creating embeddings for documents.
    """
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found at: {file_path}")
        self.file_path = file_path
        self.documents = []
        self.chunks = []

    def load_document(self):
        """Loads a PDF document."""
        print(f"Loading document from {self.file_path}...")
        loader = PyPDFLoader(self.file_path)
        self.documents = loader.load()
        print(f"Loaded {len(self.documents)} pages.")
        return self.documents

    def split_document(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Splits documents into smaller chunks."""
        if not self.documents:
            self.load_document() # Ensure document is loaded
        print(f"Splitting document into chunks (size={chunk_size}, overlap={chunk_overlap})...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        self.chunks = text_splitter.split_documents(self.documents)
        print(f"Created {len(self.chunks)} chunks.")
        return self.chunks

    def process(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Combines loading and splitting."""
        self.load_document()
        self.split_document(chunk_size, chunk_overlap)
        return self.chunks

class FinRAGAssistant:
    """
    A RAG-powered assistant for querying financial documents.
    """
    def __init__(self, chunks, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set or invalid.")
        os.environ["OPENAI_API_KEY"] = api_key
        self.chunks = chunks
        self.embeddings_model = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        self._build_system()

    def _build_system(self):
        """Builds the vector store and RAG chain."""
        print("Building vector store...")
        self.vectorstore = FAISS.from_documents(self.chunks, self.embeddings_model)
        self.retriever = self.vectorstore.as_retriever()
        print("Vector store built. Setting up RAG chain...")

        template = """You are an AI assistant specialized in analyzing financial documents.
        Use the following context to answer the question.
        If you don't know the answer, state that you don't know, but try to provide the most relevant information from the context.
        Be concise and factual.

        Context: {context}

        Question: {question}

        Answer:"""
        prompt = ChatPromptTemplate.from_template(template)

        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        print("RAG chain setup complete.")

    def query(self, question: str) -> str:
        """Queries the RAG system with a given question."""
        if not self.rag_chain:
            raise RuntimeError("RAG chain not initialized. Call _build_system first.")
        print(f"\nQuerying: {question}")
        response = self.rag_chain.invoke(question)
        return response

if __name__ == "__main__":
    # --- Configuration ---
    # IMPORTANT: Place your PDF document in the same directory as this script,
    # or provide a full path. Example: a 2023 earnings report for a public company.
    # For testing, you can place a dummy.pdf here.
    DOCUMENT_PATH = "sample_earnings_report.pdf"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Ensure this is set in your environment

    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running the script (e.g., export OPENAI_API_KEY='your_key').")
        exit(1)

    if not os.path.exists(DOCUMENT_PATH):
        print(f"Error: Document not found at '{DOCUMENT_PATH}'.")
        print("Please ensure your financial document (e.g., earnings report) is present.")
        print("For a quick test, you can create a dummy 'sample_earnings_report.pdf' with some text.")
        exit(1)

    try:
        # 1. Process the document
        processor = DocumentProcessor(DOCUMENT_PATH)
        chunks = processor.process()

        # 2. Initialize and query the RAG Assistant
        assistant = FinRAGAssistant(chunks, OPENAI_API_KEY)

        # Example Queries
        queries = [
            "What was the net income for Q4 2023?",
            "Can you summarize the company's performance in the last fiscal year?",
            "What were the key challenges mentioned in the report?",
            "Who is the CEO and what is their vision?",
            "What are the future outlooks or guidance for the next quarter?"
        ]

        for q in queries:
            answer = assistant.query(q)
            print(f"Answer: {answer}\n")

    except FileNotFoundError as e:
        print(f"Initialization error: {e}")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
