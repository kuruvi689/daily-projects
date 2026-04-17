import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class MarketIntelScout:
    """Automated lead generation and qualification system.
    This class scrapes company websites to extract key information
    for sales leads, designed with modularity and future AI integration in mind.
    """
    def __init__(self, target_urls: list[str]):
        self.target_urls = target_urls
        self.extracted_data = []

    def _fetch_page_content(self, url: str) -> str | None:
        """Fetches the HTML content of a given URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _extract_company_info(self, url: str, html_content: str) -> dict:
        """Extracts structured company information from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {"url": url, "company_name": None, "description": None, "contact_email": None, "linkedin_url": None}

        # Company Name from title or common headers
        title_tag = soup.find('title')
        if title_tag:
            data["company_name"] = title_tag.get_text(strip=True).split('|')[0].split('-')[0].strip()
        if not data["company_name"]:
            h1 = soup.find('h1')
            if h1:
                data["company_name"] = h1.get_text(strip=True)

        # Description from meta description
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            data["description"] = meta_description.get('content', '').strip()

        # Contact Email (simple regex search in body text)
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            # Filter out common image/svg emails, take the first unique one
            filtered_emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.gif', '.svg'))]
            data["contact_email"] = next(iter(set(filtered_emails)), None)

        # LinkedIn URL
        linkedin_link = soup.find('a', href=re.compile(r"linkedin.com/company|linkedin.com/in"))
        if linkedin_link:
            data["linkedin_url"] = linkedin_link.get('href')

        # Placeholder for more sophisticated extraction (e.g., using LLMs)
        # data["industry"] = self._predict_industry_with_llm(data["description"]) # Future enhancement
        return data

    def run(self) -> pd.DataFrame:
        """Orchestrates the scraping and data extraction process."""
        for url in self.target_urls:
            print(f"Processing {url}...")
            html_content = self._fetch_page_content(url)
            if html_content:
                info = self._extract_company_info(url, html_content)
                self.extracted_data.append(info)
            else:
                self.extracted_data.append({"url": url, "company_name": "N/A", "description": "N/A", "contact_email": "N/A", "linkedin_url": "N/A"})
        
        return pd.DataFrame(self.extracted_data)

if __name__ == "__main__":
    # Example usage:
    # Replace with actual target URLs of companies you want to scout.
    # For a real lead-gen scenario, these URLs would typically come from an initial discovery phase
    # (e.g., industry directories, search engine results for specific keywords).
    # The system could be extended to perform that initial URL discovery.
    example_urls = [
        "https://www.apple.com/", 
        "https://www.microsoft.com/",
        "https://www.google.com/",
        "https://www.ibm.com/"
    ]

    scout = MarketIntelScout(example_urls)
    leads_df = scout.run()

    print("\n--- Extracted Leads ---")
    print(leads_df.to_string())

    # Save to CSV for further analysis or CRM integration
    leads_df.to_csv("market_intel_leads.csv", index=False)
    print("\nLeads saved to market_intel_leads.csv")

    # This project is designed to be modular and can be extended with:
    # 1. More sophisticated data points (e.g., tech stack, employee count, recent news).
    # 2. LLM integration for semantic extraction, lead qualification, and richer insights.
    # 3. Robust scraping features like proxy rotation or headless browser support.
    # 4. Direct integration with CRM systems or databases.
