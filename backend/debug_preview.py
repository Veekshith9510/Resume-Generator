import os
import sys
import json
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from resume_generator import get_optimization_plan
from scraper import scrape_job_description

def debug_preview():
    resume_path = "backend/uploads/VEEKSHITH GULLAPUDI_RESUME.docx"
    job_url = "https://www.linkedin.com/jobs/view/4344831856" # VLink Java Developer
    
    print(f"--- 1. Scraping Job: {job_url} ---")
    job_desc = scrape_job_description(job_url)
    print(f"Scraped Length: {len(job_desc)}")
    print(f"Preview: {job_desc[:200]}...")
    
    if len(job_desc) < 100:
        print("!! WARNING: Scraped content seems too short. Scraper might be blocked.")
    
    print(f"\n--- 2. Generating Plan using {resume_path} ---")
    try:
        if not os.path.exists(resume_path):
            print(f"File not found: {resume_path}")
            return

        # Passing None for api_key will rely on os.getenv or fail gracefully
        plan = get_optimization_plan(resume_path, job_desc, api_key=None)
        
        print("\n--- 3. Optimization Plan Result ---")
        print(json.dumps(plan, indent=2))
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_preview()
