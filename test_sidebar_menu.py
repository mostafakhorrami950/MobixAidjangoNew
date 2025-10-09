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

def test_sidebar_menu_items_list(token):
    """Test the sidebar menu items list endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/sidebar-menu-items/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing sidebar menu items list endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Sidebar menu items list:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def test_user_menu(token):
    """Test the user menu endpoint"""
    headers = {
        "Authorization": f"Token {token}",
    }
    
    url = f"{BASE_URL}/api/chatbot/sidebar-menu-items/user_menu/"
    
    response = requests.get(url, headers=headers)
    
    print("Testing user menu endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("User menu items:", json.dumps(data, indent=2, ensure_ascii=False))
        return True
    else:
        print("Error:", response.text)
        return False

def main():
    """Main test function"""
    print("Testing Sidebar Menu Items API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token.")
        return
    
    print("Successfully authenticated.")
    
    # Test sidebar menu items list
    print("\n1. Testing sidebar menu items list...")
    success = test_sidebar_menu_items_list(token)
    
    # Test user menu
    print("\n2. Testing user menu...")
    success = test_user_menu(token)

if __name__ == "__main__":
    main()