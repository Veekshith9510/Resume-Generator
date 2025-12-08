from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .database import engine, Base
from .models import Base, JobPost, Resume
from .scraper import validate_url, scrape_job_description
from .resume_parser import parse_resume
from .resume_generator import generate_tailored_resume
from sqlalchemy.orm import Session
from fastapi import Depends
from .database import get_db
import shutil
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Generator API")

# CORS setup
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    url: str

class GenerateRequest(BaseModel):
    job_id: int
    resume_id: int
    api_key: str = None

@app.get("/")
def read_root():
    return {"message": "Resume Generator API is running"}

@app.post("/validate-url")
def validate_and_scrape(request: UrlRequest, db: Session = Depends(get_db)):
    if not validate_url(request.url):
        return {"valid": False, "message": "Please enter valid URL"}
    
    # Check if URL already exists
    existing_job = db.query(JobPost).filter(JobPost.url == request.url).first()
    
    # Scrape the job description
    description = scrape_job_description(request.url)
    
    if existing_job:
        existing_job.description = description
        db.commit()
        db.refresh(existing_job)
        job_post = existing_job
    else:
        # Save to DB
        job_post = JobPost(url=request.url, description=description)
        db.add(job_post)
        db.commit()
        db.refresh(job_post)
    
    return {
        "valid": True, 
        "message": "Valid URL, analyzing the Job Post",
        "data": {
            "job_id": job_post.id,
            "description_preview": description[:100] + "..." if description else "No description found"
        }
    }


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "backend/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Parse the resume
    parsed_content = parse_resume(file_path)
    
    # Save to DB
    resume = Resume(filename=file.filename, content=parsed_content, original_path=file_path)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return {
        "message": "It is uploaded successfully",
        "data": {
            "resume_id": resume.id,
            "filename": resume.filename
        }
    }

@app.post("/generate-resume")
def generate_resume(request: GenerateRequest, db: Session = Depends(get_db)):
    job_post = db.query(JobPost).filter(JobPost.id == request.job_id).first()
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    
    if not job_post or not resume:
        raise HTTPException(status_code=404, detail="Job Post or Resume not found")
    
    output_dir = "backend/generated"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"tailored_resume_{request.job_id}_{request.resume_id}.docx"
    output_path = os.path.join(output_dir, filename)
    
    _, status_message, company_name = generate_tailored_resume(resume.content, job_post.description, output_path, request.api_key)
    
    # Construct new filename if company name likely found
    final_filename = filename
    if company_name and company_name.lower() != "company":
        # Format: OriginalName_CompanyName.docx
        original_basename = os.path.splitext(resume.filename)[0]
        final_filename = f"{original_basename}_{company_name}.docx"
        new_output_path = os.path.join(output_dir, final_filename)
        
        # Rename file
        if os.path.exists(output_path):
            os.rename(output_path, new_output_path)
        
    return {
        "message": status_message,
        "download_url": f"/download-resume/{final_filename}"
    }

@app.get("/download-resume/{filename}")
def download_resume(filename: str):
    file_path = os.path.join("backend/generated", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=filename)



