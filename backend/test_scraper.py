
import requests
from bs4 import BeautifulSoup

def test_scrape():
    url = "https://www.linkedin.com/jobs/view/4344831856" # Simplified URL
    print(f"Testing URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check title to see if we hit a login wall
        print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
        
        # Try our targeting logic
        job_container = soup.find(class_="description__text") or \
                        soup.find(class_="show-more-less-html__markup") or \
                        soup.find(class_="jobs-description__content") or \
                        soup.find("article")

        if job_container:
            text = job_container.get_text(separator='\n', strip=True)
            print("--- CONTAINER FOUND ---")
            print(text[:500])
        else:
            print("--- NO CONTAINER FOUND (Fallback) ---")
            text = soup.get_text(separator='\n', strip=True)
            print(text[:500])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape()
