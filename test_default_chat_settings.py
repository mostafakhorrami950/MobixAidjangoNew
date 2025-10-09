#!/usr/bin/env python3
"""
Test script for Default Chat Settings API endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test user credentials (using the admin user we created earlier)
TEST_USERNAME = "admin"
TEST_PASSWORD = "adminpassword"

def get_auth_token():
    """Get authentication token for API access"""
    url = f"{BASE_URL}/api-token-auth/"
    data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Failed to get auth token: {response.status_code} - {response.text}")
        return None

def test_default_chat_settings_list(token):
    """Test the default chat settings list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/default-chat-settings/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing default chat settings list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} default chat settings")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First setting name: {data[0].get('name', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_active_default_chat_settings(token):
    """Test the active default chat settings endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/default-chat-settings/active/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing active default chat settings endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Active setting name: {data.get('name', 'N/A')}")
        print(f"Default chatbot: {data.get('default_chatbot_name', 'N/A')}")
        print(f"Default AI model: {data.get('default_ai_model_name', 'N/A')}")
        return True
    elif response.status_code == 404:
        print("No active default chat settings found")
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Default Chat Settings API Endpoints")
    print("=" * 40)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test default chat settings list
    print("\n1. Testing default chat settings list...")
    test_default_chat_settings_list(token)
    
    # Test active default chat settings
    print("\n2. Testing active default chat settings...")
    test_active_default_chat_settings(token)

if __name__ == "__main__":
    main()