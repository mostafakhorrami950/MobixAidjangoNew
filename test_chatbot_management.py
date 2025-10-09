import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_PHONE = "09987654321"
TEST_PASSWORD = "testpassword2"

def get_auth_token():
    """Get authentication token for API access"""
    url = f"{BASE_URL}/api-token-auth/"
    data = {
        "username": TEST_PHONE,
        "password": TEST_PASSWORD
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"Failed to get auth token: {response.status_code} - {response.text}")
        return None

def test_chatbot_stats(token):
    """Test the chatbot stats endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/chatbots/stats/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing chatbot stats endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Chatbot stats:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def test_chatbot_sessions(token, chatbot_id):
    """Test the chatbot sessions endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/chatbots/{chatbot_id}/sessions/"
    
    response = requests.get(url, headers=headers)
    
    print(f"Testing chatbot sessions endpoint for chatbot ID {chatbot_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Chatbot sessions:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def test_chatbot_usage_stats(token, chatbot_id):
    """Test the chatbot usage stats endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/chatbots/{chatbot_id}/usage_stats/"
    
    response = requests.get(url, headers=headers)
    
    print(f"Testing chatbot usage stats endpoint for chatbot ID {chatbot_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Chatbot usage stats:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def test_message_editing(token, message_id, new_content):
    """Test the message editing endpoint"""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/api/chatbot/messages/{message_id}/edit/"
    data = {
        "content": new_content
    }
    
    response = requests.patch(url, headers=headers, json=data)
    
    print(f"Testing message editing endpoint for message ID {message_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Message edit result:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Chatbot Management API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test chatbot stats
    print("\n1. Testing chatbot stats endpoint...")
    success = test_chatbot_stats(token)
    
    # Get a chatbot ID for testing
    headers = {
        "Authorization": f"Token {token}",
    }
    
    response = requests.get(f"{BASE_URL}/api/chatbot/chatbots/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('results') and len(data['results']) > 0:
            chatbot_id = data['results'][0]['id']
            
            # Test chatbot sessions
            print(f"\n2. Testing chatbot sessions endpoint for chatbot ID {chatbot_id}...")
            success = test_chatbot_sessions(token, chatbot_id)
            
            # Test chatbot usage stats
            print(f"\n3. Testing chatbot usage stats endpoint for chatbot ID {chatbot_id}...")
            success = test_chatbot_usage_stats(token, chatbot_id)
        else:
            print("No chatbots found for testing.")
    else:
        print("Failed to get chatbots list.")

if __name__ == "__main__":
    main()