import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def callToOpenAI(userprompt):
    try:
        prepromptresponse = collect_messages(userprompt, getContext('contextpreprompt.txt'))
        if "MISSING" in prepromptresponse or "missing" in prepromptresponse:
            return prepromptresponse

        return collect_messages(userprompt, getContext('contextprompt.txt'))
    except Exception as e:
        logger.error(f"Error in callToOpenAI: {str(e)}")
        raise

def get_completion_from_messages(messages, model="openai/gpt-4", temperature=0):
    try:
        # Read API key
        with open(os.path.join(os.path.dirname(__file__), "chatgptapikey.env"), "r") as f:
            api_key = f.read().strip()
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/BTankut/RevitMind",
            "X-Title": "RevitMind"
        }
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "route": "openai",
            "safe_mode": False,
            "transforms": ["middle-out"]
        }
        
        logger.info(f"Sending request to OpenRouter API with model: {model}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30  # Add timeout
        )
        
        # Handle response
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            error_detail = response.json() if response.text else "No error details"
            logger.error(f"API Error: Status {response.status_code}, Details: {error_detail}")
            raise Exception(f"OpenRouter API Error: {error_detail}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

def collect_messages(softwareprompt, userprompt):
    try:
        context = [{'role':'system', 'content': f"{softwareprompt}"}]
        context.append({'role':'user', 'content':f"{userprompt}"})
        return get_completion_from_messages(context)
    except Exception as e:
        logger.error(f"Error in collect_messages: {str(e)}")
        raise

def getContext(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading context file {filename}: {str(e)}")
        raise
