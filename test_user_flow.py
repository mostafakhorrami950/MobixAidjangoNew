import requests
import json

# Test the complete user flow: registration -> OTP verification -> login
def test_user_flow():
    base_url = "http://127.0.0.1:8000"
    api_url = f"{base_url}/api"
    
    # Step 1: Registration
    print("Step 1: Registration")
    registration_data = {
        "name": "Test User Flow",
        "phone_number": "09876543210",  # Use a new phone number
        "password": "testpassword123456",
        "password_confirm": "testpassword123456"
    }
    
    print(f"Sending registration data: {registration_data}")
    
    response = requests.post(
        f"{api_url}/accounts/register/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(registration_data)
    )
    
    print(f"Registration status: {response.status_code}")
    registration_response = response.json()
    print(f"Registration response: {registration_response}")
    
    if response.status_code != 201:
        print("Registration failed, exiting...")
        return
    
    phone_number = registration_response.get('phone_number')
    print(f"Registered phone number: {phone_number}")
    
    # Step 2: Resend OTP (to see the cooldown mechanism)
    print("\nStep 2: Resend OTP")
    resend_data = {
        "phone_number": phone_number
    }
    
    print(f"Sending resend data: {resend_data}")
    
    response = requests.post(
        f"{api_url}/accounts/resend-otp/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(resend_data)
    )
    
    print(f"Resend OTP status: {response.status_code}")
    resend_response = response.json()
    print(f"Resend OTP response: {resend_response}")
    
    # Step 3: Try to verify with an invalid OTP code
    print("\nStep 3: Verify OTP with invalid code")
    otp_data = {
        "phone_number": phone_number,
        "otp_code": "000000"  # Invalid OTP code
    }
    
    print(f"Sending OTP data: {otp_data}")
    
    response = requests.post(
        f"{api_url}/accounts/verify-otp/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(otp_data)
    )
    
    print(f"OTP verification status: {response.status_code}")
    verify_response = response.json()
    print(f"OTP verification response: {verify_response}")

if __name__ == "__main__":
    test_user_flow()