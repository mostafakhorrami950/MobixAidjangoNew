#!/usr/bin/env python3
"""
Test script for OpenRouter Request Cost Tracking API endpoints
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

def test_openrouter_costs_list(token):
    """Test the OpenRouter costs list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/openrouter-costs/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing OpenRouter costs list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} OpenRouter cost records")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First record model: {data[0].get('model_name', 'N/A')}")
            print(f"Total tokens: {data[0].get('total_tokens', 'N/A')}")
            print(f"Cost USD: {data[0].get('total_cost_usd', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_user_stats(token):
    """Test the user stats endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/openrouter-costs/user_stats/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing user stats endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total requests: {data.get('total_requests', 'N/A')}")
        print(f"Total tokens: {data.get('total_tokens', 'N/A')}")
        print(f"Total cost USD: {data.get('total_cost_usd', 'N/A')}")
        print(f"Recent requests count: {len(data.get('recent_requests', []))}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_model_stats(token):
    """Test the model stats endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/openrouter-costs/model_stats/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing model stats endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found stats for {len(data)} models")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First model: {data[0].get('model_name', 'N/A')}")
            print(f"Request count: {data[0].get('request_count', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing OpenRouter Request Cost Tracking API Endpoints")
    print("=" * 55)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test OpenRouter costs list
    print("\n1. Testing OpenRouter costs list...")
    test_openrouter_costs_list(token)
    
    # Test user stats
    print("\n2. Testing user stats...")
    test_user_stats(token)
    
    # Test model stats
    print("\n3. Testing model stats...")
    test_model_stats(token)

if __name__ == "__main__":
    main()