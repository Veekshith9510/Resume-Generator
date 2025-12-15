#!/usr/bin/env python3
"""
Local Development Server Wrapper
Runs the backend API using the local SQLite database.
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    # Get the project root directory (parent of the backend directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Change working directory to project root
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, project_root)
    
    print(f"🚀 Starting Resume Generator API from {project_root}")
    print("📂 Using Local SQLite Database (backend/main.py)")
    print("📡 Frontend should be running on http://localhost:5173")
    print("🔑 Make sure GEMINI_API_KEY is set in your environment")
    
    # Run uvicorn with the module path 'backend.main:app'
    # This correctly handles the relative imports in main.py
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
