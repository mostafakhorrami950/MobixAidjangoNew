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

def test_discount_apply(token, code, subscription_id):
    """Test the discount apply endpoint"""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/api/subscriptions/discount-codes/apply/"
    data = {
        "code": code,
        "subscription_id": subscription_id
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Testing discount code '{code}' on subscription ID {subscription_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Discount application result:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Discount Code Apply API Endpoint")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test discount apply with a valid code
    print("\n1. Testing with valid discount code 'TEST10'...")
    success = test_discount_apply(token, "TEST10", 3)  # Premium subscription
    
    if success:
        print("✓ Valid discount code application successful!")
    
    # Test discount apply with a non-existent code (should fail)
    print("\n2. Testing with non-existent discount code...")
    success = test_discount_apply(token, "NONEXISTENT", 3)
    
    if not success:
        print("✓ Expected failure for non-existent discount code - this is correct behavior!")

if __name__ == "__main__":
    main()