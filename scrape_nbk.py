"""
Simple web scraper for NBK website public information.
Scrapes key pages and saves to JSON for grounding the assistant.
"""
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


# Key NBK pages to scrape
NBK_PAGES = [
    "https://www.nbk.com/kuwait/about-us.html",
    "https://www.nbk.com/kuwait/personal.html",
    "https://www.nbk.com/kuwait/business.html",
    "https://www.nbk.com/kuwait/contact-us.html",
    "https://www.nbk.com/kuwait/branches-and-atms.html",
]


def clean_text(text):
    """Clean and normalize scraped text."""
    # Remove extra whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)


def scrape_page(url):
    """Scrape a single page and extract text content."""
    print(f"📄 Scraping: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        text = clean_text(text)
        
        # Get title
        title = soup.find('title')
        title = title.get_text() if title else url
        
        print(f"  ✅ Scraped {len(text)} characters")
        
        return {
            "url": url,
            "title": title.strip(),
            "content": text[:5000],  # Limit to 5000 chars per page
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"  ❌ Error scraping {url}: {e}")
        return None


def scrape_nbk_website(pages=None):
    """Scrape multiple NBK pages and save to JSON."""
    if pages is None:
        pages = NBK_PAGES
    
    print("=" * 60)
    print("NBK Website Scraper")
    print("=" * 60)
    
    knowledge_base = []
    
    for url in pages:
        data = scrape_page(url)
        if data:
            knowledge_base.append(data)
        time.sleep(1)  # Be polite, wait between requests
    
    # Save to JSON
    output_file = "nbk_knowledge.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ Scraped {len(knowledge_base)} pages")
    print(f"💾 Saved to: {output_file}")
    print("=" * 60)
    
    return knowledge_base


def load_nbk_knowledge():
    """Load the scraped NBK knowledge base."""
    try:
        with open("nbk_knowledge.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  nbk_knowledge.json not found. Run scraping first.")
        return []


def format_knowledge_for_prompt(knowledge_base, max_chars=8000):
    """Format knowledge base for inclusion in system prompt."""
    formatted = "=== NBK Official Information ===\n\n"
    
    total_chars = 0
    for item in knowledge_base:
        section = f"Source: {item['title']}\nURL: {item['url']}\n{item['content'][:2000]}\n\n"
        
        if total_chars + len(section) > max_chars:
            break
        
        formatted += section
        total_chars += len(section)
    
    formatted += "=== End of NBK Information ===\n"
    return formatted


if __name__ == "__main__":
    # Run the scraper
    scrape_nbk_website()
    
    # Test loading and formatting
    print("\n📖 Testing knowledge base loading...")
    kb = load_nbk_knowledge()
    formatted = format_knowledge_for_prompt(kb)
    print(f"✅ Formatted knowledge base: {len(formatted)} characters")
    print("\nPreview:")
    print(formatted[:500] + "...")
