#!/usr/bin/env python3
"""
Test script for File Upload Settings API endpoints
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

def test_file_upload_settings_list(token):
    """Test the file upload settings list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/file-upload-settings/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing file upload settings list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} file upload settings")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First setting subscription type: {data[0].get('subscription_type_name', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_file_upload_settings_for_subscription(token):
    """Test the file upload settings for subscription endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    # We'll need to get a subscription type ID first
    print("Testing file upload settings for subscription endpoint")
    print("Note: This requires a valid subscription type ID to test fully")
    return True

def main():
    """Main test function"""
    print("Testing File Upload Settings API Endpoints")
    print("=" * 40)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test file upload settings list
    print("\n1. Testing file upload settings list...")
    test_file_upload_settings_list(token)
    
    # Test file upload settings for subscription
    print("\n2. Testing file upload settings for subscription...")
    test_file_upload_settings_for_subscription(token)

if __name__ == "__main__":
    main()