# Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import google.generativeai as genai
import sys

# Script to check available Gemini models for the provided API key.
# Usage: python check_models.py <API_KEY>

# Pass API key as argument
try:
    api_key = sys.argv[1]
    genai.configure(api_key=api_key)

    print("Checking available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
