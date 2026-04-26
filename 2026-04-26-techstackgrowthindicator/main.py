import requests
from bs4 import BeautifulSoup
import json
import os

class MockLLMClient:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def classify_tech_stack_for_growth(self, tech_stack_info):
        tech_stack_str = ", ".join(tech_stack_info)
        if "Shopify" in tech_stack_str and "Google Analytics" in tech_stack_str:
            return {"growth_potential": "High", "reason": "Popular, scalable platform with analytics for tracking growth."}
        elif "WordPress" in tech_stack_str and "WooCommerce" in tech_stack_str:
            return {"growth_potential": "Medium", "reason": "Common, but growth depends on plugins and optimization."}
        else:
            return {"growth_potential": "Moderate", "reason": "Standard setup, requires deeper analysis."}

class TechStackScraper:
    def __init__(self, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"):
        self.headers = {"User-Agent": user_agent}
        self.tech_signatures = {
            "Shopify": ["shopify.com/s/files", "cdn.shopify.com", "Shopify.checkout"],
            "WooCommerce": ["wp-content/plugins/woocommerce", "data-site-context='woocommerce'"],
            "Magento": ["/static/version", "magento.js", "mage-"],
            "Google Analytics": ["googletagmanager.com/gtag/js", "analytics.js", "ga.js"],
            "Facebook Pixel": ["connect.facebook.net/en_US/fbevents.js"],
            "Klaviyo": ["cdn.klaviyo.com/js/metrics.js"]
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def identify_tech_stack(self, html_content):
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'lxml')
        found_tech = set()

        for tech, signatures in self.tech_signatures.items():
            for signature in signatures:
                if signature in html_content:
                    found_tech.add(tech)
                elif soup.find(lambda tag: tag.get('src') and signature in tag['src']) or \
                     soup.find(lambda tag: tag.get('href') and signature in tag['href']):
                    found_tech.add(tech)
        
        if soup.find("meta", {"content": "Shopify"}):
             found_tech.add("Shopify")
        if soup.find("link", {"rel": "generator", "href": "https://wordpress.org/"}):
             found_tech.add("WordPress")
        if soup.find("meta", {"name": "generator", "content": "WooCommerce"}):
            found_tech.add("WooCommerce")

        return list(found_tech)

class LeadGenerator:
    def __init__(self, scraper, ai_client):
        self.scraper = scraper
        self.ai_client = ai_client
        self.results = []

    def process_url(self, url):
        print(f"Processing {url}...")
        html = self.scraper.fetch_page(url)
        tech_stack = self.scraper.identify_tech_stack(html)
        
        ai_analysis = self.ai_client.classify_tech_stack_for_growth(tech_stack)
        
        self.results.append({
            "url": url,
            "tech_stack": tech_stack,
            "ai_growth_analysis": ai_analysis
        })
        print(f"  -> Tech Stack: {tech_stack}")
        print(f"  -> AI Analysis: {ai_analysis}")

    def generate_leads(self, urls):
        for url in urls:
            self.process_url(url)
        return self.results

    def save_results_to_json(self, filename="leads_with_growth_potential.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        print(f"Results saved to {filename}")

if __name__ == "__main__":
    target_urls = [
        "https://www.shopify.com/plus", 
        "https://woocommerce.com/", 
        "https://magento.com/",
        "https://example.com"
    ]
    
    # In a real scenario, you might read from a file like this:
    # try:
    #     with open("target_ecomm_urls.txt", "r") as f:
    #         target_urls = [line.strip() for line in f if line.strip()]
    # except FileNotFoundError:
    #     print("target_ecomm_urls.txt not found. Using default example URLs.")

    scraper = TechStackScraper()
    ai_client = MockLLMClient(api_key=os.getenv("OPENAI_API_KEY")) # Replace with actual OpenAI client if using

    lead_gen = LeadGenerator(scraper, ai_client)
    leads = lead_gen.generate_leads(target_urls)
    lead_gen.save_results_to_json()
