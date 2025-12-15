import json
import boto3
import logging

logger = logging.getLogger()

s3_client = boto3.client('s3')

def read_json(bucket, key):
    """
    Reads a JSON file from S3 and returns the dictionary.
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error reading JSON from S3 {bucket}/{key}: {str(e)}")
        raise

def write_json(bucket, key, data):
    """
    Writes a dictionary as a JSON file to S3.
    """
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
    except Exception as e:
        logger.error(f"Error writing JSON to S3 {bucket}/{key}: {str(e)}")
        raise

def upload_file(bucket, key, body, content_type='application/octet-stream'):
    """
    Uploads raw content bytes/string to S3.
    """
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=content_type
        )
    except Exception as e:
        logger.error(f"Error uploading file to S3 {bucket}/{key}: {str(e)}")
        raise

def generate_presigned_url(bucket, key, expiration=3600):
    """
    Generates a presigned URL for downloading a file.
    """
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': key},
                                                    ExpiresIn=expiration)
        return response
    except Exception as e:
        logger.error(f"Error generating presigned URL for {bucket}/{key}: {str(e)}")
        raise
