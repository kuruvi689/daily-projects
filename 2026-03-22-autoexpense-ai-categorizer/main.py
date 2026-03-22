import os
import pandas as pd
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    """Handles interactions with the OpenAI LLM."""
    def __init__(self, api_key=None, model="gpt-3.5-turbo", temperature=0.2):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found. Set it in .env or pass directly.")
        openai.api_key = self.api_key
        self.model = model
        self.temperature = temperature

    def get_completion(self, prompt, max_tokens=60):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except openai.error.OpenAIError as e:
            print(f"Error communicating with OpenAI: {e}")
            return "" # Return empty string on error

class ExpenseCategorizer:
    """Categorizes financial transactions using an LLM and predefined rules."""
    def __init__(self, llm_service, categories_file='config/categories.json'):
        self.llm_service = llm_service
        self.categories_file = categories_file
        self.categories = self._load_categories()

    def _load_categories(self):
        """Loads user-defined categories and keywords."""
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r') as f:
                return json.load(f)
        return {
            "Food & Dining": [],
            "Transportation": [],
            "Housing": [],
            "Utilities": [],
            "Entertainment": [],
            "Shopping": [],
            "Health": [],
            "Income": [],
            "Savings": [],
            "Other": []
        }

    def _save_categories(self):
        """Saves current categories to the config file."""
        os.makedirs(os.path.dirname(self.categories_file), exist_ok=True)
        with open(self.categories_file, 'w') as f:
            json.dump(self.categories, f, indent=4)

    def add_custom_category(self, category_name, keywords=None):
        """Adds or updates a custom category with optional keywords."""
        if category_name not in self.categories:
            self.categories[category_name] = []
        if keywords:
            for kw in keywords:
                if kw not in self.categories[category_name]:
                    self.categories[category_name].append(kw)
        self._save_categories()
        print(f"Category '{category_name}' updated.")

    def _get_category_prompt(self, description):
        """Generates the LLM prompt for categorization."""
        category_list = ", ".join(self.categories.keys())
        return f"Categorize the following financial transaction description into one of these categories: {category_list}. Only return the category name. If none fit perfectly, choose the closest or 'Other'.\nDescription: '{description}'\nCategory:"

    def categorize_transaction(self, description):
        """Applies keyword-based rules first, then falls back to LLM."""
        description_lower = description.lower()

        # Rule-based categorization
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category

        # LLM-based categorization
        llm_category = self.llm_service.get_completion(self._get_category_prompt(description))

        # Validate LLM output against known categories, default to 'Other' if invalid
        if llm_category in self.categories:
            return llm_category
        
        # Attempt to find a partial match (e.g., LLM returns 'Food' for 'Food & Dining')
        for cat_name in self.categories.keys():
            if llm_category.lower() in cat_name.lower():
                return cat_name

        return "Other" # Fallback

class FinancialDataAnalyzer:
    """Provides basic insights from categorized financial data."""
    def __init__(self, dataframe):
        self.df = dataframe

    def get_spending_summary(self):
        """Returns a summary of total spending per category."""
        if 'Amount' not in self.df.columns or 'Category' not in self.df.columns:
            return pd.Series(dtype=float)
        
        # Assuming 'Amount' column contains negative values for expenses and positive for income
        expenses_df = self.df[self.df['Amount'] < 0].copy() # Ensure we're working on a copy
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        summary = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        return summary

    def get_top_expenses(self, n=5):
        """Returns the top N individual expense transactions."""
        if 'Amount' not in self.df.columns or 'Description' not in self.df.columns:
            return pd.DataFrame()
        
        top_n = self.df[self.df['Amount'] < 0].nsmallest(n, 'Amount') # nsmallest for most negative (largest expenses)
        return top_n[['Description', 'Amount', 'Category']]

def run_categorization(input_csv_path, output_csv_path):
    """Main function to orchestrate the categorization process."""
    if not os.path.exists(input_csv_path):
        print(f"Error: Input CSV '{input_csv_path}' not found.")
        return

    print(f"Loading transactions from {input_csv_path}...")
    try:
        transactions_df = pd.read_csv(input_csv_path)
        if 'Description' not in transactions_df.columns or 'Amount' not in transactions_df.columns:
            print("Error: Input CSV must contain 'Description' and 'Amount' columns.")
            return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    llm = LLMService()
    categorizer = ExpenseCategorizer(llm)

    print("Categorizing transactions...")
    transactions_df['Category'] = transactions_df['Description'].apply(categorizer.categorize_transaction)

    print("Categorization complete. Saving results...")
    transactions_df.to_csv(output_csv_path, index=False)
    print(f"Categorized data saved to {output_csv_path}")

    analyzer = FinancialDataAnalyzer(transactions_df)
    print("\n--- Financial Insights ---")
    print("\nSpending Summary:")
    print(analyzer.get_spending_summary().to_string())
    print("\nTop 5 Individual Expenses:")
    print(analyzer.get_top_expenses().to_string())

    print("\n\nExample usage of adding a custom category and keywords (uncomment to run):\n")
    # categorizer.add_custom_category("Coffee Shops", ["starbucks", "coffee bean"])
    # print("Re-categorizing with new rule (only for demonstration, normally re-run whole process if rules change):")
    # transactions_df['Category_New'] = transactions_df['Description'].apply(categorizer.categorize_transaction)
    # print(transactions_df[['Description', 'Category', 'Category_New']].head())

if __name__ == "__main__":
    # Create a dummy CSV for testing if it doesn't exist
    if not os.path.exists('data/transactions.csv'):
        os.makedirs('data', exist_ok=True)
        dummy_data = [
            {"Date": "2023-01-01", "Description": "Starbucks Coffee", "Amount": -5.25},
            {"Date": "2023-01-02", "Description": "Grocery Store Run", "Amount": -78.90},
            {"Date": "2023-01-03", "Description": "Salary Payment", "Amount": 3500.00},
            {"Date": "2023-01-04", "Description": "Uber Ride", "Amount": -15.50},
            {"Date": "2023-01-05", "Description": "Netflix Subscription", "Amount": -12.99},
            {"Date": "2023-01-06", "Description": "Dinner at Italian Restaurant", "Amount": -65.00},
            {"Date": "2023-01-07", "Description": "Online Shopping - Amazon", "Amount": -45.75},
            {"Date": "2023-01-08", "Description": "Utility Bill - Electricity", "Amount": -80.00},
            {"Date": "2023-01-09", "Description": "Transfer to Savings", "Amount": -200.00},
            {"Date": "2023-01-10", "Description": "Dental Checkup", "Amount": -120.00}
        ]
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_csv('data/transactions.csv', index=False)
        print("Created dummy 'data/transactions.csv' for demonstration.")

    # Ensure config directory exists
    os.makedirs('config', exist_ok=True)

    input_csv = 'data/transactions.csv'
    output_csv = 'data/categorized_transactions.csv'
    run_categorization(input_csv, output_csv)
