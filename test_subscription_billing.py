import requests
import json
from datetime import datetime, timedelta

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

def test_financial_transactions_summary(token):
    """Test the financial transactions summary endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/subscriptions/financial-transactions/summary/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing financial transactions summary endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Financial transactions summary:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def test_financial_transactions_by_date_range(token):
    """Test the financial transactions by date range endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    url = f"{BASE_URL}/api/subscriptions/financial-transactions/by_date_range/?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}"
    
    response = requests.get(url, headers=headers)
    
    print("Testing financial transactions by date range endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Financial transactions by date range:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Subscription and Billing API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test discount apply with a valid code
    print("\n1. Testing discount apply with valid code...")
    success = test_discount_apply(token, "TEST10", 3)  # Premium subscription
    
    # Test discount validation
    print("\n2. Testing discount validation...")
    success = test_discount_validation(token, "TEST10", 3)  # Premium subscription
    
    # Test my discount uses
    print("\n3. Testing my discount uses...")
    success = test_my_discount_uses(token)
    
    # Test financial transactions summary
    print("\n4. Testing financial transactions summary...")
    success = test_financial_transactions_summary(token)
    
    # Test financial transactions by date range
    print("\n5. Testing financial transactions by date range...")
    success = test_financial_transactions_by_date_range(token)

if __name__ == "__main__":
    main()