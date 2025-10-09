#!/usr/bin/env python3
"""
Test script for Limitation Messages API endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test user credentials (using the admin user we just created)
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

def test_limitation_messages_list(token):
    """Test the limitation messages list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/limitation-messages/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing limitation messages list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} limitation messages")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First message type: {data[0].get('limitation_type', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_active_limitation_messages(token):
    """Test the active limitation messages endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/limitation-messages/active/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing active limitation messages endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} active limitation messages")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First active message type: {data[0].get('limitation_type', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_limitation_message_by_type(token):
    """Test the limitation message by type endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/limitation-messages/by_type/?type=token_limit"
    
    response = requests.get(url, headers=headers)
    
    print("Testing limitation message by type endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Token limit message: {data.get('title', 'N/A')} - {data.get('message', 'N/A')}")
        return True
    elif response.status_code == 404:
        print("Token limit message not found")
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Limitation Messages API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test limitation messages list
    print("\n1. Testing limitation messages list...")
    test_limitation_messages_list(token)
    
    # Test active limitation messages
    print("\n2. Testing active limitation messages...")
    test_active_limitation_messages(token)
    
    # Test limitation message by type
    print("\n3. Testing limitation message by type...")
    test_limitation_message_by_type(token)

if __name__ == "__main__":
    main()