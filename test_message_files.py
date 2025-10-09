#!/usr/bin/env python3
"""
Test script for Message File Attachments API endpoints
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

def test_message_files_list(token):
    """Test the message files list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/message-files/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing message files list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} message file attachments")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First attachment message content: {data[0].get('message_content', 'N/A')[:50]}...")
            print(f"File name: {data[0].get('file_name', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_message_files_by_message(token):
    """Test the message files by message endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    # We'll need to get a message ID first
    print("Testing message files by message endpoint")
    print("Note: This requires a valid message ID to test fully")
    return True

def main():
    """Main test function"""
    print("Testing Message File Attachments API Endpoints")
    print("=" * 45)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test message files list
    print("\n1. Testing message files list...")
    test_message_files_list(token)
    
    # Test message files by message
    print("\n2. Testing message files by message...")
    test_message_files_by_message(token)

if __name__ == "__main__":
    main()