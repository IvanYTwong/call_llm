#!/usr/bin/env python3
"""
Debug script to test OpenRouter API connection
"""

import os
from dotenv import load_dotenv
import requests

def debug_api_connection():
    """Debug the API connection step by step."""
    
    print("🔍 OpenRouter API Debug")
    print("=" * 40)
    
    # Step 1: Check .env file loading
    print("\n1. Loading .env file...")
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if api_key:
        print(f"✅ API key loaded: {api_key[:20]}...")
    else:
        print("❌ No API key found in environment")
        return
    
    # Step 2: Test API endpoint
    print("\n2. Testing API endpoint...")
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API connection successful!")
            models = response.json()
            print(f"Available models: {len(models.get('data', []))}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    # Step 3: Test simple chat completion
    print("\n3. Testing chat completion...")
    chat_url = "https://openrouter.ai/api/v1/chat/completions"
    
    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(chat_url, headers=headers, json=payload, timeout=30)
        print(f"Chat Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ Chat successful! Response: {content[:100]}...")
        else:
            print(f"❌ Chat Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat error: {e}")

if __name__ == "__main__":
    debug_api_connection()

