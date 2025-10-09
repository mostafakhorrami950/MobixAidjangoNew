#!/usr/bin/env python3
"""
Test script for Image Generation Usage Tracking API endpoints
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

def test_image_generation_usage_list(token):
    """Test the image generation usage list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/image-generation-usage/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing image generation usage list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} image generation usage records")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First record user: {data[0].get('user_name', 'N/A')}")
            print(f"Daily images count: {data[0].get('daily_images_count', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def test_user_stats(token):
    """Test the user stats endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/image-generation-usage/user_stats/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing user stats endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} usage records for current user")
        if data and isinstance(data, list) and len(data) > 0:
            print(f"First record subscription type: {data[0].get('subscription_type_name', 'N/A')}")
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Image Generation Usage Tracking API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test image generation usage list
    print("\n1. Testing image generation usage list...")
    test_image_generation_usage_list(token)
    
    # Test user stats
    print("\n2. Testing user stats...")
    test_user_stats(token)

if __name__ == "__main__":
    main()