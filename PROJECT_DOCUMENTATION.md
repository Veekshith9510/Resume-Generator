# Project Documentation: Resume Generator
*By Veekshith Gullapudi*

## 1. Project Requirements

The **Resume Generator** is a web application designed to tailor resumes to specific job descriptions using AI.

### Functional Requirements
- **Job Description Parsing**: The system must be able to scrape and extract text from job postings (LinkedIn, Monster).
- **Resume Parsing**: The system updates support parsing text from uploaded resumes in PDF (`.pdf`) and Word (`.docx`) formats.
- **AI Enhancement**: Utilizes Google Gemini AI to rewrite resume bullet points, summaries, and skills to align with the target job description.
- **File Generation**: Generates a downloadable tailored resume (DOCX format) with an optimized filename (e.g., `OriginalName_CompanyName.docx`).
- **History/Storage**: Stores job postings and uploaded resumes in a local SQLite database.

### Non-Functional Requirements
- **Performance**: Resume generation should complete within reasonable time limits (dependent on AI API latency).
- **Usability**: Simple UI for URL input and file upload.

## 2. Prerequisites

Before running the project, ensure you have the following installed:

### System Tools
- **Node.js** (v18+ recommended) & **npm**
- **Python** (v3.9+ recommended)

### API Keys
- **Google Gemini API Key**: Required for the AI features. You must obtain an API key from Google AI Studio and set it as an environment variable `GEMINI_API_KEY`.

### Python Dependencies (Backend)
Since `requirements.txt` is not present, install the following packages:
```bash
pip install fastapi uvicorn sqlalchemy google-generativeai requests beautifulsoup4 pypdf python-docx python-multipart
```

### Node Dependencies (Frontend)
Dependencies are managed via `package.json`.
- `react`
- `vite`
- `axios`
- `mammoth`

## 3. Implementation Plan (Architecture)

The project follows a client-server architecture.

### Backend (`/backend`)
- **Framework**: `FastAPI` for high-performance Async I/O.
- **Database**: `SQLite` (via `SQLAlchemy` ORM) to store `JobPost` and `Resume` records.
- **AI Integration**: `copilot.py` encapsulates the logic for interacting with Google's Gemini Pro model (`gemini-flash-latest`). It handles prompt engineering for resume rewriting and company name extraction.
- **Scraper**: `scraper.py` uses `requests` and `BeautifulSoup` to fetch job descriptions.
- **Parser**: `resume_parser.py` extracts raw text from PDF and DOCX files using `pypdf` and `python-docx`.

### Frontend (`/frontend`)
- **Framework**: React with Vite build tool.
- **Styling**: Standard CSS (`App.css`).
- **API Interaction**: Uses `axios` to communicate with the FastAPI backend.
- **UI Flow**:
    1.  User enters Job URL -> Backend validates & scrapes.
    2.  User uploads Resume -> Backend parses & saves.
    3.  User clicks "Generate" -> Backend invokes AI & provides download link.

## 4. Execution Plan

### Step 1: Start the Backend
1.  Navigate to the `backend` directory (or root).
2.  Set your API key:
    *   Mac/Linux: `export GEMINI_API_KEY="your_key_here"`
    *   Windows: `set GEMINI_API_KEY="your_key_here"`
3.  Run the server:
    ```bash
    uvicorn backend.main:app --reload
    ```
    The server will start at `http://127.0.0.1:8000`.

### Step 2: Start the Frontend
1.  Open a new terminal.
2.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
3.  Install dependencies (first time only):
    ```bash
    npm install
    ```
4.  Run the development server:
    ```bash
    npm run dev
    ```
    The UI will be accessible at `http://localhost:5173` (typically).

## 5. Bug Fixes & Known Issues

- **CORS Configuration**: The backend currently hardcodes `http://localhost:5173` and `http://localhost:3000` as allowed origins. If Vite runs on a different port, requests will fail.
    *   *Fix*: Update `backend/main.py` origins list or use a wildcard in dev (not recommended for prod).
- **Scraping Limitations**: The `requests` library cannot scrape dynamic JavaScript-heavy sites (like some LinkedIn views).
    *   *Fix*: Move to `Selenium` or `Playwright` for robust scraping.
- **Resume Formatting**: The current parser extracts *text only*. The generated resume usually loses the original complex layout and returns a simple Markdown-to-DOCX structure.
    *   *Fix*: Implement a template-based generation system or modify the DOCX XML directly to preserve styles.

## 6. Future Enhancements

1.  **Authentication**: Add user login to save resumes and history per user.
2.  **Dashboard**: A "My Resumes" page to view past generated resumes.
3.  **Template Selection**: Allow users to choose from different resume templates (Modern, Classic, ATS-Friendly).
4.  **Cover Letter Generation**: Add a feature to generate a matching cover letter.
5.  **Direct LinkedIn Integration**: Use a browser extension to capture the job description directly from the active tab to bypass scraping blocks.

## 7. Vulnerabilities

- **Input Validation**: While `validate_url` exists, `copilot.py` processing of AI output for filenames uses basic sanitization. Malformed AI output *could* theoretically cause issues, though `os.path.join` mitigates path traversal.
- **API Key Security**: The API key is read from env vars (good), but ensure `.env` files are not committed to version control.
- **Injection Attacks**: The `scraper` fetches content from arbitrary URLs. While `BeautifulSoup` parses it, ensure no malicious scripts are stored/executed if the frontend renders raw HTML (currently it seems to handle text).

## 8. Deployment

### Backend Deployment
- **Docker**: Create a `Dockerfile` for the python environment.
- **Platform**: Deploy to Render, Railway, or Heroku.
- **Environment**: Set `GEMINI_API_KEY` in the cloud provider's secrets manager.

### Frontend Deployment
- **Build**: Run `npm run build` to create static assets in `dist/`.
- **Platform**: Deploy the `dist` folder to Vercel, Netlify, or GitHub Pages.
- **Configuration**: Ensure the frontend knows the production Backend URL (use environment variables like `VITE_API_URL` instead of hardcoded localhost).
