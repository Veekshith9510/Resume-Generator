import boto3
import os
import json
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

RESUME_BUCKET = os.environ.get("RESUME_BUCKET")
SECRET_ARN = os.environ.get("SECRET_ARN")

def get_secret(secret_name_or_arn):
    try:
        get_secret_value_response = secrets_client.get_secret_value(
            SecretId=secret_name_or_arn
        )
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return None

    if 'SecretString' in get_secret_value_response:
        return get_secret_value_response['SecretString']
    return None

def get_gemini_api_key():
    # optimized to check env first (for local testing), then secrets manager
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    if SECRET_ARN:
        secret_str = get_secret(SECRET_ARN)
        if secret_str:
            try:
                # Assuming secret is stored as JSON {"GEMINI_API_KEY": "..."} or just the string
                secret_dict = json.loads(secret_str)
                return secret_dict.get("GEMINI_API_KEY")
            except json.JSONDecodeError:
                return secret_str
    return None

def upload_file_to_s3(file_path, object_name):
    try:
        s3_client.upload_file(file_path, RESUME_BUCKET, object_name)
        return True
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False

def get_presigned_url(object_name, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': RESUME_BUCKET,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
        return response
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

def download_file_from_s3(object_name, file_path):
    try:
        s3_client.download_file(RESUME_BUCKET, object_name, file_path)
        return True
    except ClientError as e:
        print(f"Error downloading from S3: {e}")
        return False
