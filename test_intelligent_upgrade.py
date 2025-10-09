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

def test_intelligent_upgrade(token, subscription_id):
    """Test the intelligent upgrade endpoint"""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/api/subscriptions/subscription-management/{subscription_id}/intelligent_upgrade/"
    response = requests.post(url, headers=headers)
    
    print(f"Testing intelligent upgrade to subscription ID {subscription_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Upgrade calculation:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Intelligent Upgrade API Endpoint")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test intelligent upgrade with subscription ID 3 (Premium)
    success = test_intelligent_upgrade(token, 3)
    
    if success:
        print("\n🎉 Intelligent upgrade endpoint is working correctly!")
    else:
        print("\n⚠️  Intelligent upgrade endpoint has issues.")

if __name__ == "__main__":
    main()