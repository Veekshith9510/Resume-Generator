import google.generativeai as genai
import sys

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
