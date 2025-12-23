import os
import re
from docx import Document
from unittest.mock import MagicMock, patch
import json

# Import the actual components
try:
    from resume_generator import generate_tailored_resume
    from copilot import ResumeCopilot
except ImportError:
    import sys
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from resume_generator import generate_tailored_resume
    from copilot import ResumeCopilot

def run_deep_debug(resume_path, job_desc):
    print(f"\n==========================================")
    print(f"🚀 STARTING DEEP DEBUG FOR: {os.path.basename(resume_path)}")
    print(f"==========================================\n")

    if not os.path.exists(resume_path):
        print(f"❌ ERROR: Resume file not found at {resume_path}")
        return

    # 1. Inspect Document Structure
    print("--- [STEP 1] Inspecting Document Paragraphs ---")
    doc = Document(resume_path)
    experience_headers = [
        "experience", "professional experience", "work history", 
        "employment history", "work experience", "career history"
    ]
    summary_headers = ["summary", "professional summary", "objective", "profile", "professional profile"]
    stop_headers = ["education", "skills", "projects", "technical skills", "certifications", "awards", "languages", "volunteering"]
    
    in_experience = False
    in_summary = False
    bullets_found = 0
    summary_paras = 0
    
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if not text: continue
        
        lower_text = text.lower()
        is_header = False
        
        # Header Detection Logic (Match resume_generator.py)
        if p.style.name.startswith('Heading') or (len(text) < 50 and text.isupper()) or (p.runs and p.runs[0].bold and len(text) < 50):
            if any(h in lower_text for h in experience_headers):
                print(f"  [FOUND] Experience Header at L{i}: '{text}' (Style: {p.style.name})")
                in_experience = True
                in_summary = False
                is_header = True
            elif any(h in lower_text for h in summary_headers):
                print(f"  [FOUND] Summary Header at L{i}: '{text}' (Style: {p.style.name})")
                in_summary = True
                in_experience = False
                is_header = True
            elif (in_experience or in_summary) and any(sh in lower_text for sh in stop_headers):
                print(f"  [STOP] Section End Header at L{i}: '{text}' (Style: {p.style.name})")
                in_experience = False
                in_summary = False
                is_header = True
        
        if in_experience and not is_header:
            is_list = False
            try:
                if p._p.pPr is not None and p._p.pPr.numPr is not None: is_list = True
            except: pass
            
            if 'list' in p.style.name.lower() or is_list or text.startswith(('•', '-', '–', '*', '·', '◦')):
                bullets_found += 1
                print(f"    -> [EXP BULLET {bullets_found}] '{text[:100]}...'")
        
        if in_summary and not is_header:
             summary_paras += 1
             print(f"    -> [SUMMARY PARA {summary_paras}] '{text[:100]}...'")

    print(f"\n--- [SUMMARY] Found {bullets_found} exp bullets and {summary_paras} summary paras. ---\n")

if __name__ == "__main__":
    import sys
    RESUME = sys.argv[1] if len(sys.argv) > 1 else "backend/uploads/VEEKSHITH GULLAPUDI_RESUME_main.docx"
    SAMPLE_JD = "Senior Java Full Stack Developer with experience in Spring Boot, Angular, and AWS."
    run_deep_debug(RESUME, SAMPLE_JD)
