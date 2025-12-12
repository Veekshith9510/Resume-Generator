import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum

# Local imports (assuming all files are in the same directory in Lambda)
try:
    from . import lambda_db as db
    from . import aws_utils
    from .scraper import validate_url, scrape_job_description
    from .resume_parser import parse_resume
    from .resume_generator import generate_tailored_resume
except ImportError:
    # Fallback for when running as top-level script (in Lambda root)
    import lambda_db as db
    import aws_utils
    from scraper import validate_url, scrape_job_description
    from resume_parser import parse_resume
    from resume_generator import generate_tailored_resume

app = FastAPI(title="Resume Generator API (Serverless)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    url: str

class GenerateRequest(BaseModel):
    job_id: str
    resume_id: str
    api_key: str = None

@app.get("/")
def read_root():
    return {"message": "Serverless Resume Generator API is running"}

@app.post("/validate-url")
def validate_and_scrape(request: UrlRequest):
    if not validate_url(request.url):
        return {"valid": False, "message": "Please enter valid URL"}
    
    # Check DB
    existing_job = db.get_job_post_by_url(request.url)
    if existing_job:
        job_post = existing_job
        description = job_post.get('description', '')
    else:
        description = scrape_job_description(request.url)
        job_post = db.create_job_post(request.url, description)
    
    if not job_post:
         raise HTTPException(status_code=500, detail="Database Error")

    return {
        "valid": True, 
        "message": "Valid URL, analyzing the Job Post",
        "data": {
            "job_id": job_post['id'],
            "description_preview": description[:100] + "..." if description else "No description found"
        }
    }

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    # Use /tmp for lambda storage
    upload_dir = "/tmp" 
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    parsed_content = parse_resume(file_path)
    
    # Upload to S3
    s3_key = f"uploads/{file.filename}"
    if not aws_utils.upload_file_to_s3(file_path, s3_key):
         raise HTTPException(status_code=500, detail="S3 Upload Failed")
         
    # Clean up tmp
    os.remove(file_path)

    # Save to DynamoDB
    resume = db.create_resume_record(file.filename, parsed_content, s3_key)
    if not resume:
        raise HTTPException(status_code=500, detail="Database Save Failed")
    
    return {
        "message": "It is uploaded successfully",
        "data": {
            "resume_id": resume['id'],
            "filename": resume['filename']
        }
    }

@app.post("/generate-resume")
def generate_resume(request: GenerateRequest):
    job_post = db.get_job_post_by_id(request.job_id)
    resume = db.get_resume_by_id(request.resume_id)
    
    if not job_post or not resume:
        raise HTTPException(status_code=404, detail="Job Post or Resume not found")
    
    # Get API Key
    api_key = aws_utils.get_gemini_api_key()
    if request.api_key:
        api_key = request.api_key
        
    output_dir = "/tmp"
    filename = f"tailored_resume_{request.job_id}_{request.resume_id}.docx"
    output_path = os.path.join(output_dir, filename)
    
    # Generate
    _, status_message, company_name = generate_tailored_resume(
        resume['content'], 
        job_post['description'], 
        output_path, 
        api_key
    )
    
    # Rename if company name found
    final_filename = filename
    if company_name and company_name.lower() != "company":
        original_basename = os.path.splitext(resume['filename'])[0]
        final_filename = f"{original_basename}_{company_name}.docx"
        new_output_path = os.path.join(output_dir, final_filename)
        if os.path.exists(output_path):
            os.rename(output_path, new_output_path)
            output_path = new_output_path

    # Upload Generated file to S3
    s3_key = f"generated/{final_filename}"
    if not aws_utils.upload_file_to_s3(output_path, s3_key):
         raise HTTPException(status_code=500, detail="S3 Upload Failed")
         
    # Get Presigned URL
    download_url = aws_utils.get_presigned_url(s3_key)
    
    return {
        "message": status_message,
        "download_url": download_url, # Client can use this directly
        "filename": final_filename
    }

@app.get("/download-resume/{filename}")
def download_resume(filename: str):
    # This endpoint might not be needed if generate-resume returns the direct S3 URL.
    # But for compatibility or abstracting S3 bucket structure...
    
    # We assume 'generated/' prefix based on logic above
    s3_key = f"generated/{filename}"
    url = aws_utils.get_presigned_url(s3_key)
    if not url:
        raise HTTPException(status_code=404, detail="File not found")
        
    return {"url": url}

handler = Mangum(app)
