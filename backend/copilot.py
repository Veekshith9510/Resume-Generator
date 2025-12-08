import os
import google.generativeai as genai

class ResumeCopilot:
    def __init__(self, api_key: str = None):
        # Prefer environment variable if not passed directly
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None

    def enhance_content(self, original_text: str, job_description: str) -> str:
        """
        Enhances the resume content based on the job description.
        """
        if not self.model:
            # Fallback if no API key is present
            return f"{original_text}\n\n[AI ENHANCEMENT SKIPPED: Missing API Key]\n\n"

        prompt = f"""
        You are an expert resume writer. I will provide you with my original resume content and a job description.
        Your task is to rewrite the candidate's resume to specifically target the Job Description provided.
        
        Tailoring Instructions (CRITICAL):
        1. **Job Title Analysis**: Identify the Job Title and Company from the Job Description.
        2. **Professional Summary**: Rewrite the Professional Summary (or Objective) to explicitly mention the targeted Job Title and Company, and highlight 2-3 key achievements that fit this specific role.
        3. **Experience Enhancements**:
            - Keep the Company Name, Job Title, and Dates exactly as in the original resume.
            - **Rewrite the bullet points** for each role to emphasize skills and achievements that are most relevant to this specific Job Description.
            - Use specific keywords and terminology from the Job Description in the bullet points.
            - If a bullet point is completely irrelevant to the new role, remove it or deprioritize it.
            - ensuring the meaning doesn't change
        4. **Skills**: Add relevant technical or soft skills found in the Job Description (if the candidate's background supports them) and prioritize them.
        
        IMPORTANT FORMATTING INSTRUCTIONS:
        1. Keep the resume in the same format as the original resume (headers, order).
        2. Use Markdown headers (#, ##) for section titles.
        3. Use bullet points (-) for list items.
        4. Use **bold** for emphasis on key skills or metrics.
        5. Do NOT use asterisks (*) for bullet points, use hyphens (-).
        6. Do NOT use code blocks.
        7. Keep the layout professional and clean.
        8. Keep the Education section as is.
        
        Job Description:
        {job_description}
        
        Original Resume:
        {original_text}
        
        Please provide the full rewritten resume content in clean Markdown.
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=8192
                )
            )
            return response.text
        except Exception as e:
            print(f"Copilot Error: {e}")
            return original_text + f"\n\n[AI ENHANCEMENT FAILED: {str(e)}]"

    def extract_company_name(self, job_description: str) -> str:
        """
        Extracts the company name from the job description.
        """
        if not self.model:
            return "Company"

        prompt = f"""
        Identify the company name from the following job description. 
        Return ONLY the company name. If not found, return "Company".
        Do not include any other text or punctuation.
        
        Job Description:
        {job_description}
        """

        try:
            response = self.model.generate_content(prompt)
            company_name = response.text.strip()
            # Basic cleanup to ensure filename safety
            safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_', '-')).strip()
            return safe_name.replace(' ', '_')
        except Exception:
            return "Company"
