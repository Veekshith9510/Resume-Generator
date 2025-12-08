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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Basic extraction logic - this might need refinement based on actual page structure
        # For now, we'll extract all text from the body, or specific containers if known
        
        # Attempt to find common job description containers
        # LinkedIn often uses 'description' class or similar
        # Monster might vary
        
        # Fallback: get all text
        text = soup.get_text(separator='\n', strip=True)
        
        # Limit text length to avoid processing too much irrelevant info
        return text[:5000] 
        
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return ""

