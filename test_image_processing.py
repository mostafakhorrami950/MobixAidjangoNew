#!/usr/bin/env python3
"""
Test script for Image Processing and Vision Capabilities API endpoints
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

def test_vision_settings_list(token):
    """Test the vision settings list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/vision-settings/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing vision settings list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} vision settings")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First setting name: {data[0].get('name', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_uploaded_images_list(token):
    """Test the uploaded images list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/images/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing uploaded images list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} uploaded images")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First image uploaded at: {data[0].get('uploaded_at', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_upload_image(token):
    """Test the image upload endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    # We'll need to create a session first to test this properly
    print("Testing image upload endpoint")
    print("Note: This requires a valid session ID to test fully")
    return True

def main():
    """Main test function"""
    print("Testing Image Processing and Vision Capabilities API Endpoints")
    print("=" * 60)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test vision settings list
    print("\n1. Testing vision settings list...")
    test_vision_settings_list(token)
    
    # Test uploaded images list
    print("\n2. Testing uploaded images list...")
    test_uploaded_images_list(token)
    
    # Test image upload
    print("\n3. Testing image upload...")
    test_upload_image(token)

if __name__ == "__main__":
    main()