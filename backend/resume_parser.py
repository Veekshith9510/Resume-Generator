# Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import os
from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text content from a PDF file.
    Iterates through all pages and concatenates the text.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text content from a DOCX file.
    Iterates through all paragraphs and concatenates the text.
    """
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def parse_resume(file_path: str) -> str:
    """
    Main parser function that determines file type and calls the appropriate extractor.
    Supports .pdf and .docx extensions.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format"

