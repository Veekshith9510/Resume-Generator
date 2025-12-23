# Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import os
import google.generativeai as genai
import json

class ResumeCopilot:
    def __init__(self, api_key: str = None):
        """
        Initializes the ResumeCopilot with an API key.
        Checks for the API key in the environment variables if not provided directly.
        Configures the Gemini generative AI model.
        """
        # Prefer environment variable if not passed directly
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None

    def enhance_content(self, original_text: str, job_description: str) -> str:
        """
        DEPRECATED: Use optimize_bullet_points instead.
        """
        return f"[DEPRECATED] Content enhancement skipped."

    def optimize_all_content(self, summary_text: str, experience_entries: list[dict], job_description: str) -> dict:
        """
        Batches all resume components into a SINGLE AI request to avoid rate limits.
        """
        if not self.model:
            return None

        print(f"DEBUG: Optimization Request - JD Length: {len(job_description)}")
        print(f"DEBUG: JD Preview: {job_description[:200]}...")

        # Prepare a structured payload for the AI
        payload = {
            "summary": summary_text,
            "entries": [{"id": i, "header": e["header"], "bullets": e["bullets"]} for i, e in enumerate(experience_entries)]
        }

        prompt = f"""
        You are a top-tier resume architect. 
        
        Job Description:
        {job_description}

        Current Resume Content (JSON):
        {json.dumps(payload, indent=2)}

        Task: 
        1. Identify the hiring company from the Job Description.
        2. Optimize the "summary" to be a high-impact, 3-4 sentence professional summary targeted at the JD.
        3. For EACH experience entry:
           - Optimize the existing bullets for impact and relevance.
           - ADD 2-3 NEW high-impact bullets that align the candidate's background with the JD (e.g. ServiceNow, Cloud, leadership).
           - ENSURE all bullets are SHORT, CRISP, and TO THE POINT.
        4. Make sure the resume is optimized for the hiring company.
        5. The new bullet points should be relevant to the job description.
        6. The new Bullet points shoud be Quantifiable Metrics, Architectural Decision-Making, Cross-Functional Leadership, Business Alignment
        7. Once the new bullet points are generated, cross check with the existing bullet points and remove any duplicates.
        STRICT RULES:
        - Return ONLY a JSON object with keys: "company_name" (string), "summary" (string) and "entries" (list of objects with "id" and "optimized_bullets" list).
        - Each bullet MUST be a single line.
        - DO NOT HALLUCINATE brand new jobs.
        - Preserve dates and company names.
        
        Output format:
        {{
          "company_name": "...",
          "summary": "...",
          "entries": [
            {{ "id": 0, "optimized_bullets": ["...", "...", "..."] }},
            ...
          ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip().replace('```json', '').replace('```', '').strip()
            result = json.loads(clean_text)
            return result
        except Exception as e:
            print(f"DEBUG: AI Batch Error - {e}")
            return None

    def extract_company_name(self, job_description: str) -> str:
        """
        Extracts the company name from the job description.
        """
        if not self.model or not job_description:
            return "Company"

        prompt = f"Extract only the company name from this job description. If not found, return 'Company'.\n\nJob Description:\n{job_description}"
        try:
            response = self.model.generate_content(prompt)
            name = response.text.strip()
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
            return safe_name.replace(' ', '_')
        except:
            return "Company"
