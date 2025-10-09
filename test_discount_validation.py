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

def test_discount_validation(token, code, subscription_id):
    """Test the discount validation endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/subscriptions/discount-codes/validate_code/?code={code}&subscription_id={subscription_id}"
    
    response = requests.get(url, headers=headers)
    
    print(f"Testing discount code validation for '{code}' on subscription ID {subscription_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Discount validation result:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def test_my_discount_uses(token):
    """Test the my discount uses endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/subscriptions/discount-codes/my_discount_uses/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing my discount uses endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("My discount uses:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Discount Code Validation API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test discount validation with a valid code
    print("\n1. Testing discount validation with valid code...")
    success = test_discount_validation(token, "TEST10", 3)  # Premium subscription
    
    if success:
        print("✓ Discount validation endpoint working!")
    
    # Test my discount uses
    print("\n2. Testing my discount uses endpoint...")
    success = test_my_discount_uses(token)
    
    if success:
        print("✓ My discount uses endpoint working!")

if __name__ == "__main__":
    main()