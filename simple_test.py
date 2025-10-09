import requests

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

def test_subscription_types(token):
    """Test the subscription types endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    response = requests.get(f"{BASE_URL}/api/subscriptions/subscription-types/", headers=headers)
    print(f"Subscription types endpoint status: {response.status_code}")
    if response.status_code == 200:
        subscriptions = response.json()
        print(f"Raw subscriptions data: {subscriptions}")
        print(f"Type of subscriptions: {type(subscriptions)}")
        print(f"Length of subscriptions: {len(subscriptions)}")
        if isinstance(subscriptions, list) and len(subscriptions) > 0:
            print("First subscription:", subscriptions[0])
        else:
            print("No subscription types found or not a list")
    else:
        print("Error:", response.text)

def main():
    """Main test function"""
    print("Testing Subscription Types Endpoint")
    print("=" * 40)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print(f"Successfully authenticated.")
    
    # Test subscription types endpoint
    test_subscription_types(token)

if __name__ == "__main__":
    main()