# AutoExpense AI-Categorizer

## Project Description

AutoExpense AI-Categorizer is a Python-based tool designed to automate the categorization of financial transactions using a combination of keyword-based rules and Large Language Models (LLMs). This project aims to significantly reduce the manual effort involved in personal or business finance management by intelligently assigning categories to raw transaction data (e.g., from bank statements or credit card exports). Beyond simple categorization, it provides basic financial insights, helping users understand their spending patterns and identify high-leverage opportunities for financial optimization.

This tool is built with modularity and SaaS potential in mind, designed to function as a micro-service that can be integrated into larger financial infrastructure or offered as a standalone utility.

## Strategic Alignment

This project directly addresses multiple pillars of the Teddy³ strategic goal architecture:

1.  **AI Mastery & Agentic Systems:**
    *   **Focus:** LLM orchestration for intelligent categorization, leveraging advanced AI capabilities to interpret unstructured transaction descriptions. This builds mastery in prompt engineering and integrating LLMs into functional systems.
    *   **Strategic Outcome:** Mastering the "weapons" of the 2026 economy by applying AI to automate complex data interpretation tasks.

2.  **Financial Independence & Wealth Infrastructure:**
    *   **Focus:** Financial data analysis and algorithmic calculation (implicit in categorization logic). It automates a critical component of expense tracking and provides foundational data for portfolio tracking and wealth management.
    *   **Strategic Outcome:** Building the "engine" that replaces the salary bribe by automating the infrastructure for understanding and managing personal finances, laying groundwork for future algorithmic financial tools.

3.  **Technical Architectural Skills:**
    *   **Focus:** Advanced Python mastery, modular design, and robust data processing. The clear separation of concerns (LLM service, categorizer, analyzer) demonstrates strong architectural principles.
    *   **Strategic Outcome:** Building a "fortress" that functions with 100% autonomy by creating self-contained, reusable, and performant components.

4.  **Strategic Thinking & Decision Frameworks (Indirect):**
    *   **Focus:** By providing clear, categorized financial data and initial insights, it enables better decision-making regarding spending, budgeting, and investment strategies. The insights generator serves as a rudimentary decision-support tool.
    *   **Strategic Outcome:** Sharpening the "mind" by providing actionable data that can lead to identifying high-leverage financial adjustments.

## SaaS Potential

This project has significant micro-service potential. Imagine a service where users upload their CSV bank statements (or link a financial API), and the `ExpenseCategorizer` module runs as a backend service, returning categorized data and insights. This could be offered as a premium subscription for `$5/month` for:

*   **Automated Categorization:** Eliminating tedious manual work.
*   **Customizable Rules:** Users define their own categories and keywords.
*   **AI-Driven Accuracy:** Leveraging LLMs for nuanced and flexible categorization beyond simple keyword matching.
*   **Financial Insights Dashboard (Future):** Building upon the `FinancialDataAnalyzer` to offer deeper visualizations and predictive analytics.

## Modularity

The project is designed with modularity at its core:

*   `LLMService`: A standalone module for interacting with OpenAI (or other LLM providers), easily swappable.
*   `ExpenseCategorizer`: Contains the core logic for categorization, independent of data input/output methods.
*   `FinancialDataAnalyzer`: Focuses solely on deriving insights from *already categorized* data.
*   Data Ingestion/Output: Handled separately, currently with CSV, but extensible to Google Sheets, APIs, etc.

Each component can be reused in different contexts or scaled independently as a micro-service.

## Features

*   **Intelligent Categorization:** Uses OpenAI's LLM to categorize transaction descriptions into user-defined or default categories.
*   **Rule-Based Overrides:** Supports keyword-based rules for high-precision categorization, prioritizing user preferences.
*   **Custom Category Management:** Allows users to define new categories and associate keywords.
*   **CSV Data Ingestion & Output:** Reads transaction data from CSV files and outputs categorized data to a new CSV.
*   **Basic Financial Insights:** Provides a summary of spending by category and identifies top individual expenses.
*   **Environment Variable Support:** Securely manages API keys using `.env` files.

## Installation

1.  **Clone the repository:**
    bash
    git clone <repository-url>
    cd autoexpense-ai-categorizer
    

2.  **Create a virtual environment (recommended):**
    bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    

3.  **Install dependencies:**
    bash
    pip install -r requirements.txt
    

4.  **Set up OpenAI API Key:**
    *   Create a `.env` file in the root directory of the project.
    *   Add your OpenAI API key to the file:
        
        OPENAI_API_KEY="your_openai_api_key_here"
        

## Usage

1.  **Prepare your input data:**
    *   Ensure you have a CSV file (e.g., `data/transactions.csv`) with at least two columns: `Description` (text describing the transaction) and `Amount` (numeric value, typically negative for expenses, positive for income).
    *   A dummy `data/transactions.csv` will be created if it doesn't exist upon first run.

2.  **Configure categories (optional):**
    *   Edit `config/categories.json` to define your preferred categories and associate keywords for rule-based matching. For example:
        
        {
            "Food & Dining": ["restaurant", "cafe", "groceries"],
            "Transportation": ["uber", "lyft", "gas station"],
            "Shopping": ["amazon", "target"],
            "Utilities": ["electricity", "water", "internet"]
        }
        
    *   The `add_custom_category` method can also be used programmatically.

3.  **Run the categorizer:**
    bash
    python main.py
    

4.  **Review output:**
    *   A new CSV file (`data/categorized_transactions.csv`) will be created with an additional `Category` column.
    *   Financial insights (spending summary, top expenses) will be printed to the console.

## Example `data/transactions.csv`

csv
Date,Description,Amount
2023-01-01,Starbucks Coffee,-5.25
2023-01-02,Grocery Store Run,-78.90
2023-01-03,Salary Payment,3500.00
2023-01-04,Uber Ride,-15.50
2023-01-05,Netflix Subscription,-12.99


## Future Enhancements

*   **Google Sheets Integration:** Directly read/write from/to Google Sheets using `gspread`.
*   **Customizable LLM Prompts:** Allow users to fine-tune the prompts sent to the LLM.
*   **Advanced Insight Generation:** Implement more sophisticated analytics (e.g., trend analysis, budget vs. actual, anomaly detection).
*   **Web UI/API Endpoint:** Develop a simple Flask/FastAPI interface to expose the categorization as a micro-service.
*   **User Feedback Loop:** Implement a mechanism for users to correct LLM categorizations, which can then be used to fine-tune the model or update keyword rules.
*   **Multiple LLM Providers:** Support for Anthropic, Hugging Face models, etc.
*   **RAG for Context:** Use RAG to pull in personalized spending history or user-defined examples to improve categorization accuracy.
