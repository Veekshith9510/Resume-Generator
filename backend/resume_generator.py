from docx import Document
import os
from .copilot import ResumeCopilot

def generate_tailored_resume(original_content: str, job_description: str, output_path: str, api_key: str = None) -> tuple[str, str, str]:
    """
    Generates a tailored resume based on the original content and job description.
    Saves the result to output_path.
    """
    try:
        # AI Enhancement
        copilot = ResumeCopilot(api_key)
        tailored_content = copilot.enhance_content(original_content, job_description)
        
        # Extract Company Name
        company_name = copilot.extract_company_name(job_description)
        
        status_message = "Resume generated successfully with AI enhancement"
        if "[AI ENHANCEMENT SKIPPED" in tailored_content:
            status_message = "Resume generated without AI enhancement (Missing API Key)"
        elif "[AI ENHANCEMENT FAILED" in tailored_content:
            status_message = "Resume generated, but AI enhancement failed"

        doc = Document()
        
        doc.add_heading('Tailored Resume', 0)
        
        # Markdown Rendering Logic
        import re
        
        def add_formatted_paragraph(document, text, style=None):
            p = document.add_paragraph(style=style)
            # Split by double asterisks for bolding
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    p.add_run(part)

        for line in tailored_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('# '):
                doc.add_heading(line[2:], level=1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], level=2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], level=3)
            elif line.startswith('- '):
                add_formatted_paragraph(doc, line[2:], style='List Bullet')
            else:
                add_formatted_paragraph(doc, line)
        
        doc.save(output_path)
        return output_path, status_message, company_name
    except Exception as e:
        print(f"Error generating resume: {e}")
        return "", f"Error generating resume: {str(e)}", ""

