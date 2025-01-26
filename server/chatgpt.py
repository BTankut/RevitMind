import openai
import os
import requests
import json

def callToOpenAI(userprompt):
    setOpenAiKey()
    prepromptresponse = collect_messages(userprompt, getContext('contextpreprompt.txt'))
    if "MISSING" in prepromptresponse or "missing" in prepromptresponse:
        return prepromptresponse

    return collect_messages(userprompt, getContext('contextprompt.txt'))

def get_completion_from_messages(messages, model="openai/gpt-4", temperature=0):
    with open(os.path.join(os.path.dirname(__file__), "chatgptapikey.env"), "r") as f:
        api_key = f.read().strip()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/BTankut/RevitMind",
        "X-Title": "RevitMind"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "route": "openai",
        "safe_mode": False
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def collect_messages(softwareprompt, userprompt):
    context = [{'role':'system', 'content': f"{softwareprompt}"}]
    context.append({'role':'user', 'content':f"{userprompt}"})
    response = get_completion_from_messages(context)
    return response

def setOpenAiKey():
    # OpenRouter API key'i zaten get_completion_from_messages içinde kullanılıyor
    pass

def getContext(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
        return f.read()
