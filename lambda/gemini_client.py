import os
import json
import time
import requests
import logging
import boto3

logger = logging.getLogger()

class GeminiClient:
    def __init__(self, secret_name=None, region_name='us-east-1'):
        self.api_key = self._get_api_key(secret_name, region_name)
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"

    def _get_api_key(self, secret_name, region_name):
        if not secret_name:
            # Fallback for local dev if env var is set directly
            return os.environ.get("GEMINI_API_KEY")
            
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        
        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in get_secret_value_response:
                secret = json.loads(get_secret_value_response['SecretString'])
                return secret.get("GEMINI_API_KEY")
        except Exception as e:
            logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
            raise

    def generate_content(self, prompt, max_retries=3):
        """
        Generates content using Gemini API with exponential backoff.
        """
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        headers = {'Content-Type': 'application/json'}
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                # Extract text from response
                if 'candidates' in result and result['candidates']:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    logger.warning(f"Unexpected response format from Gemini: {result}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) # Exponential backoff: 1s, 2s, 4s
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries reached for Gemini API")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error calling Gemini API: {str(e)}")
                raise

