import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger()

def scrape_job_description(url):
    """
    Scrapes the text content from the given URL.
    """
    if not url:
        return ""
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit length to avoid token limits if necessary, though Gemini has large context
        return text[:50000] 
        
    except requests.RequestException as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        # Return empty string or partial content on failure, so process doesn't completely die if scraping fails
        return f"Error scraping job description: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error scraping URL {url}: {str(e)}")
        return ""
