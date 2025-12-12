import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

JOB_POSTS_TABLE = os.environ.get("JOB_POSTS_TABLE")
RESUMES_TABLE = os.environ.get("RESUMES_TABLE")

def get_job_table():
    return dynamodb.Table(JOB_POSTS_TABLE)

def get_resume_table():
    return dynamodb.Table(RESUMES_TABLE)

def create_job_post(url, description):
    table = get_job_table()
    job_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    item = {
        'id': job_id,
        'url': url,
        'description': description,
        'created_at': timestamp
    }
    
    try:
        table.put_item(Item=item)
        return item
    except ClientError as e:
        print(f"Error creating job post: {e}")
        return None

def get_job_post_by_url(url):
    table = get_job_table()
    try:
        # Since 'id' is Hash Key, we have to Scan or Query using GSI if we want efficient search by URL.
        # For simplicity without GSIs in Terraform (to keep it simple as generated), we Scan. 
        # CAUTION: Scan is expensive in prod. Ideally adding GSI on URL.
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('url').eq(url)
        )
        if response['Items']:
            return response['Items'][0]
        return None
    except ClientError as e:
        print(f"Error getting job post: {e}")
        return None

def update_job_post(job_id, description):
    table = get_job_table()
    try:
        response = table.update_item(
            Key={'id': job_id},
            UpdateExpression="set description=:d",
            ExpressionAttributeValues={':d': description},
            ReturnValues="ALL_NEW"
        )
        return response.get('Attributes')
    except ClientError as e:
        print(f"Error updating job post: {e}")
        return None

def get_job_post_by_id(job_id):
    table = get_job_table()
    try:
        response = table.get_item(Key={'id': job_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting job post by ID: {e}")
        return None

def create_resume_record(filename, content, s3_key):
    table = get_resume_table()
    resume_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    item = {
        'id': resume_id,
        'filename': filename,
        'content': content,
        'original_path': s3_key, # Using S3 key instead of local path
        'created_at': timestamp
    }
    
    try:
        table.put_item(Item=item)
        return item
    except ClientError as e:
        print(f"Error creating resume record: {e}")
        return None

def get_resume_by_id(resume_id):
    table = get_resume_table()
    try:
        response = table.get_item(Key={'id': resume_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting resume: {e}")
        return None
