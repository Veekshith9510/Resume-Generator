def get_resume_rewrite_prompt(original_resume_text, job_description_text):
    """
    Constructs the prompt for rewriting the resume.
    """
    return f"""
    You are an expert Resume Writer and Career Coach.
    
    Task: Rewrite the following resume to better match the provided job description.
    
    Guidelines:
    1. Highlight relevant skills and experiences that align with the job requirements.
    2. Use strong action verbs and professional language.
    3. Maintain the truthfulness of the original resume; do not invent experiences.
    4. Improve readability and formatting (Use markdown).
    5. Optimization: Incorporate keywords from the job description for ATS optimization.
    
    ---
    JOB DESCRIPTION:
    {job_description_text}
    
    ---
    ORIGINAL RESUME:
    {original_resume_text}
    
    ---
    OUTPUT (Markdown format):
    """
