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

def test_usage_endpoints(token):
    """Test the new usage statistics API endpoints"""
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # Test results storage
    results = {}
    
    print("Testing Usage Statistics API Endpoints")
    print("=" * 40)
    
    # Usage statistics endpoints
    usage_endpoints = [
        ("/api/subscriptions/subscription-management/usage_statistics/", "GET"),
        ("/api/subscriptions/subscription-management/usage_summary/", "GET"),
        ("/api/subscriptions/subscription-management/usage_cards/", "GET"),
    ]
    
    for endpoint, method in usage_endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"  Testing {method} {endpoint}...")
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers)
            
            print(f"    Status: {response.status_code} - {'✓' if response.status_code == 200 else '✗'}")
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    "status_code": response.status_code,
                    "success": True,
                    "data": data
                }
                print(f"    Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            else:
                results[endpoint] = {
                    "status_code": response.status_code,
                    "success": False,
                    "error": response.text
                }
                print(f"    Error: {response.text[:100]}...")
        except Exception as e:
            results[endpoint] = {
                "status_code": 0,
                "success": False,
                "error": str(e)
            }
            print(f"    Exception: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print("USAGE STATISTICS API SUMMARY")
    print("=" * 40)
    
    success_count = 0
    total_count = len(results)
    
    for endpoint, result in results.items():
        if result['success']:
            success_count += 1
        else:
            print(f"✗ {endpoint}: {result['status_code']} - {result.get('error', 'Error')}")
    
    print(f"\nSuccessful tests: {success_count}/{total_count}")
    print(f"Success rate: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 All Usage Statistics API endpoints are working correctly!")
    else:
        print("⚠️  Some Usage Statistics API endpoints have issues.")
    
    return results

def main():
    """Main test function"""
    print("Usage Statistics API Endpoint Testing")
    print("=" * 40)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token. Please make sure the server is running and credentials are correct.")
        return
    
    print(f"Successfully authenticated.")
    
    # Test usage endpoints
    results = test_usage_endpoints(token)
    
    # Save results to file
    with open('usage_statistics_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to usage_statistics_test_results.json")

if __name__ == "__main__":
    main()