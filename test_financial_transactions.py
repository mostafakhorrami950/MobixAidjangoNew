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

def test_financial_transactions_list(token):
    """Test the financial transactions list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/subscriptions/financial-transactions/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing financial transactions list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Financial transactions:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def test_financial_transaction_detail(token, transaction_id):
    """Test the financial transaction detail endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/subscriptions/financial-transactions/{transaction_id}/"
    
    response = requests.get(url, headers=headers)
    
    print(f"Testing financial transaction detail endpoint for ID {transaction_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Financial transaction detail:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Financial Transactions API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test financial transactions list
    print("\n1. Testing financial transactions list...")
    success = test_financial_transactions_list(token)
    
    if success:
        print("✓ Financial transactions list endpoint working!")
    
    # Test financial transaction detail (if we have any transactions)
    print("\n2. Testing financial transaction detail...")
    # First get the list to find a transaction ID
    headers = {
        "Authorization": f"Token {token}",
    }
    
    response = requests.get(f"{BASE_URL}/api/subscriptions/financial-transactions/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('results') and len(data['results']) > 0:
            transaction_id = data['results'][0]['id']
            success = test_financial_transaction_detail(token, transaction_id)
            if success:
                print("✓ Financial transaction detail endpoint working!")
        else:
            print("No financial transactions found for testing detail endpoint.")
    else:
        print("Failed to get financial transactions list.")

if __name__ == "__main__":
    main()