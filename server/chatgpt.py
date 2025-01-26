import os
import requests
import json
import logging
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def callToOpenAI(userprompt):
    try:
        logger.debug("Starting callToOpenAI with prompt: %s", userprompt)
        
        # Ensure input is string
        if isinstance(userprompt, bytes):
            userprompt = userprompt.decode('utf-8')
            logger.debug("Decoded bytes prompt to: %s", userprompt)
            
        # First check with preprompt
        logger.info("Checking preprompt")
        prepromptresponse = collect_messages(userprompt, getContext('contextpreprompt.txt'))
        if isinstance(prepromptresponse, bytes):
            prepromptresponse = prepromptresponse.decode('utf-8')
        prepromptresponse = prepromptresponse.strip()
        logger.debug("Preprompt response: %s", prepromptresponse)
        
        # If it's a MISSING response, return it
        if prepromptresponse.startswith("MISSING-"):
            logger.info("Returning MISSING response: %s", prepromptresponse)
            return prepromptresponse
            
        # If preprompt says YES or anything else, proceed with main prompt
        logger.info("Proceeding with main prompt")
        response = collect_messages(userprompt, getContext('contextprompt.txt'))
        if isinstance(response, bytes):
            response = response.decode('utf-8')
        logger.debug("Final response: %s", response)
        return response
        
    except Exception as e:
        logger.error("Error in callToOpenAI: %s", str(e), exc_info=True)
        raise

def get_completion_from_messages(messages, model="openai/gpt-4", temperature=0):
    try:
        logger.debug("Starting API request with model: %s", model)
        
        # Read API key
        api_key_path = os.path.join(os.path.dirname(__file__), "chatgptapikey.env")
        logger.debug("Reading API key from: %s", api_key_path)
        try:
            with open(api_key_path, "r") as f:
                api_key = f.read().strip()
        except Exception as e:
            logger.error("Failed to read API key: %s", str(e))
            raise Exception("API key not found or invalid")
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000
        }
        
        logger.info("Sending request to OpenRouter API")
        logger.debug("Request data: %s", json.dumps(data, indent=2))
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        # Handle response
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            logger.debug("Received successful response: %s", content)
            return content
        else:
            error_detail = response.json() if response.text else "No error details"
            logger.error("API Error: Status %d, Details: %s", response.status_code, error_detail)
            raise Exception(f"OpenRouter API Error: {error_detail}")
            
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", str(e), exc_info=True)
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        raise

def collect_messages(softwareprompt, userprompt):
    try:
        logger.debug("Collecting messages - Software prompt: %s, User prompt: %s", 
                    softwareprompt[:100] + "...", userprompt)
        
        # Ensure inputs are strings
        if isinstance(softwareprompt, bytes):
            softwareprompt = softwareprompt.decode('utf-8')
        if isinstance(userprompt, bytes):
            userprompt = userprompt.decode('utf-8')
            
        context = [{'role':'system', 'content': f"{softwareprompt}"}]
        context.append({'role':'user', 'content':f"{userprompt}"})
        
        logger.debug("Prepared context messages: %s", json.dumps(context, indent=2))
        return get_completion_from_messages(context)
    except Exception as e:
        logger.error("Error in collect_messages: %s", str(e), exc_info=True)
        raise

def getContext(filename):
    try:
        file_path = os.path.join(os.path.dirname(__file__), filename)
        logger.debug("Reading context from: %s", file_path)
        
        with open(file_path, "r") as f:
            content = f.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            logger.debug("Read context file successfully, length: %d", len(content))
            return content
    except Exception as e:
        logger.error("Error reading context file %s: %s", filename, str(e), exc_info=True)
        raise
