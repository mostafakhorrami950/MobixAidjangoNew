import requests
import json

# Request a new OTP code
login_url = "http://127.0.0.1:8000/api/accounts/login/"
login_data = {
    "phone_number": "09123456789"
}

headers = {
    "Content-Type": "application/json",
}

try:
    response = requests.post(login_url, data=json.dumps(login_data), headers=headers)
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code == 200:
        # Now try to verify the OTP
        verify_url = "http://127.0.0.1:8000/api/accounts/verify-otp/"
        # We'll need to check the server logs or database to get the actual OTP code
        print("\nPlease check the server logs or database for the OTP code and update the test script.")
        
except Exception as e:
    print(f"Error: {e}")