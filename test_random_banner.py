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

def test_random_banner_endpoint(token):
    """Test the random banner API endpoint"""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/api/core/advertising-banners/random/"
    print(f"Testing GET {url}...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Random banner result:", json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print("Error:", response.text)
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Random Advertising Banner API Endpoint")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print(f"Successfully authenticated.")
    
    # Test random banner endpoint
    success = test_random_banner_endpoint(token)
    
    if success:
        print("\n🎉 Random banner API endpoint is working correctly!")
    else:
        print("\n⚠️  Random banner API endpoint has issues.")

if __name__ == "__main__":
    main()