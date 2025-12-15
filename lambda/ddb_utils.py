import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
dynamodb = boto3.resource('dynamodb')

def get_item(table_name, key):
    """
    Retrieves an item from DynamoDB by key.
    key should be a dict, e.g., {'id': '123'}
    """
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key=key)
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting item from DynamoDB table {table_name}: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting item from DynamoDB {table_name}: {str(e)}")
        raise

def put_item(table_name, item):
    """
    Puts an item into DynamoDB.
    """
    try:
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
    except ClientError as e:
        logger.error(f"Error putting item to DynamoDB table {table_name}: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error putting item to DynamoDB {table_name}: {str(e)}")
        raise
