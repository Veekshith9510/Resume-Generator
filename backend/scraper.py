# Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import requests
from bs4 import BeautifulSoup
import re

def validate_url(url: str) -> bool:
    """
    Validates if the provided URL is a supported job posting link.
    Currently supports LinkedIn and Monster URLs.
    """
    linkedin_pattern = r"https?://(www\.)?linkedin\.com/.*"
    monster_pattern = r"https?://(www\.)?monster\.com/.*"
    
    if re.match(linkedin_pattern, url) or re.match(monster_pattern, url):
        return True
    return False

def scrape_job_description(url: str) -> str:
    """
    Scrapes the text content of the job description from the given URL.
    Uses a browser-like User-Agent to avoid basic bot detection.
    Extracts all text from the page body and truncates it to 5000 chars.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Basic extraction logic - this might need refinement based on actual page structure
        # For now, we'll extract all text from the body, or specific containers if known
        
        # Try to find specific job description containers for better quality
        # LinkedIn specific classes
        job_container = soup.find(class_="description__text") or \
                        soup.find(class_="show-more-less-html__markup") or \
                        soup.find(class_="jobs-description__content") or \
                        soup.find("article")

        if job_container:
            text = job_container.get_text(separator='\n', strip=True)
            print(f"DEBUG: Scraper found targeted container. Length: {len(text)}")
        else:
            # Fallback: get all text but try to skip head/scripts
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.decompose()
            text = soup.get_text(separator='\n', strip=True)
            print(f"DEBUG: Scraper used fallback. Length: {len(text)}")
        
        # Limit text length to avoid processing too much irrelevant info
        return text[:10000] # Increased limit to ensure we capture full JDs
        
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return ""

