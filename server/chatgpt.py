import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def callToOpenAI(userprompt):
    try:
        # Ensure input is string
        if isinstance(userprompt, bytes):
            userprompt = userprompt.decode('utf-8')
            
        # First check with preprompt
        prepromptresponse = collect_messages(userprompt, getContext('contextpreprompt.txt'))
        if isinstance(prepromptresponse, bytes):
            prepromptresponse = prepromptresponse.decode('utf-8')
        prepromptresponse = prepromptresponse.strip()
        
        # If preprompt says YES, get the greeting from contextprompt
        if prepromptresponse == "YES":
            contextprompt = getContext('contextprompt.txt')
            # Find the matching greeting
            for line in contextprompt.split('\n'):
                if userprompt.lower() in line.lower() and 'respond with:' in line.lower():
                    return line.split('respond with:')[1].strip()
            
            # If no matching greeting found, use default
            return "Merhaba! Size nasıl yardımcı olabilirim?"
        
        # If it's a MISSING response, return it
        if prepromptresponse.startswith("MISSING-"):
            return prepromptresponse
            
        # If preprompt didn't say YES or MISSING, proceed with main prompt
        response = collect_messages(userprompt, getContext('contextprompt.txt'))
        if isinstance(response, bytes):
            response = response.decode('utf-8')
        return response
        
    except Exception as e:
        logger.error(f"Error in callToOpenAI: {str(e)}")
        raise

def get_completion_from_messages(messages, model="openai/gpt-4", temperature=0):
    try:
        # Read API key
        with open(os.path.join(os.path.dirname(__file__), "chatgptapikey.env"), "r") as f:
            api_key = f.read().strip()
        
        # Prepare headers - Keep it simple
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare request data - Basic format
        data = {
            "model": model,
            "messages": messages
        }
        
        logger.info(f"Sending request to OpenRouter API with model: {model}")
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
            return content
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
        # Ensure inputs are strings
        if isinstance(softwareprompt, bytes):
            softwareprompt = softwareprompt.decode('utf-8')
        if isinstance(userprompt, bytes):
            userprompt = userprompt.decode('utf-8')
            
        context = [{'role':'system', 'content': f"{softwareprompt}"}]
        context.append({'role':'user', 'content':f"{userprompt}"})
        return get_completion_from_messages(context)
    except Exception as e:
        logger.error(f"Error in collect_messages: {str(e)}")
        raise

def getContext(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
            content = f.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return content
    except Exception as e:
        logger.error(f"Error reading context file {filename}: {str(e)}")
        raise
