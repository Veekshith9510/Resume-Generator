import json
import os
import logging
import uuid
from s3_utils import read_json, write_json, upload_file, generate_presigned_url
from ddb_utils import get_item
from url_scraper import scrape_job_description
from gemini_client import GeminiClient
from prompt_templates import get_resume_rewrite_prompt

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment Variables
GEMINI_SECRET_NAME = os.environ.get('GEMINI_SECRET_NAME')
RESUME_BUCKET = os.environ.get('RESUME_BUCKET')
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET')
DDB_TABLE = os.environ.get('DDB_TABLE')

def handler(event, context):
    """
    Lambda Handler Entry Point
    """
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # 1. Parse Input
        # Support both API Gateway proxy integration and direct invocation
        body = {}
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event

        resume_id = body.get('resume_id')
        job_url = body.get('job_url')
        
        if not resume_id or not job_url:
            raise ValueError("Missing resume_id or job_url")
            
        logger.info(f"Processing resume_id: {resume_id} for job_url: {job_url}")

        # 2. Get Metadata from DynamoDB
        # We assume the frontend uploaded the file to S3 and saved metadata to DDB
        # Metadata should contain the S3 key of the uploaded resume
        resume_metadata = get_item(DDB_TABLE, {'id': resume_id})
        if not resume_metadata:
             raise ValueError(f"Resume metadata not found for id: {resume_id}")
             
        s3_key = resume_metadata.get('s3_key') # e.g., "uploads/123.pdf" or "uploads/123.txt"
        # For this version, let's assume the resume text content is also stored/extracted,
        # OR we interpret the file from S3. 
        # To simplify: assume user uploaded a JSON or text file, OR we extract text here.
        # For simplicity in this step: assume we read raw text or a text file.
        # If it's a PDF, we'd need PyPDF2 (layer required). 
        # Let's assume the frontend extracts text OR the file is plain text for now as per "resume text" requirement.
        
        # Reading text from S3
        # If key ends with .json, parse it. If .txt, read it.
        try:
             # Just read content as string
             import boto3
             s3 = boto3.client('s3')
             obj = s3.get_object(Bucket=RESUME_BUCKET, Key=s3_key)
             resume_content = obj['Body'].read().decode('utf-8')
        except Exception as e:
             raise ValueError(f"Could not read resume file from S3: {str(e)}")

        # 3. Scrape Job Description
        job_description_text = scrape_job_description(job_url)
        if not job_description_text:
             logger.warning("Job description scraping failed or returned empty.")
             job_description_text = "No job description available."

        # 4. Generate Content with Gemini
        client = GeminiClient(secret_name=GEMINI_SECRET_NAME)
        prompt = get_resume_rewrite_prompt(resume_content, job_description_text)
        
        # Call AI
        new_resume_text = client.generate_content(prompt)
        
        if not new_resume_text:
            raise RuntimeError("Gemini returned no content")
            
        # 5. Save Output to S3
        output_key = f"generated/{resume_id}_{uuid.uuid4().hex[:8]}.md"
        upload_file(OUTPUT_BUCKET, output_key, new_resume_text, content_type='text/markdown')
        
        # 6. Generate Download URL
        download_url = generate_presigned_url(OUTPUT_BUCKET, output_key)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "success",
                "output_s3_path": f"s3://{OUTPUT_BUCKET}/{output_key}",
                "download_url": download_url
            })
        }

    except ValueError as ve:
        logger.error(f"Validation Error: {str(ve)}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"status": "error", "message": str(ve)})
        }
    except Exception as e:
        logger.error(f"Internal Error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"status": "error", "message": "Internal Server Error"})
        }
