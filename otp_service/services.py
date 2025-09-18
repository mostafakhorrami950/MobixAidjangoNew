import requests
import json
import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import OTP
from accounts.models import User

class OTPService:
    @staticmethod
    def generate_otp_code():
        """Generate a 6-digit OTP code"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def send_otp_via_ipanel(phone_number, otp_code):
        """
        Send OTP code via IPANEL SMS service
        Returns True if successful, False otherwise
        """
        url = "https://edge.ippanel.com/v1/api/send"
        
        payload = {
            "sending_type": "pattern",
            "from_number": settings.IPANEL_FROM_NUMBER,
            "code": settings.IPANEL_PATTERN_CODE,
            "recipients": [phone_number],
            "params": {
                "code": otp_code
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': settings.IPANEL_API_KEY
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('meta', {}).get('status') == True:
                return True, response_data
            else:
                return False, response_data
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def create_and_send_otp(user):
        """
        Create a new OTP for the user and send it via SMS
        Returns (success, message)
        """
        # Generate a new OTP code
        otp_code = OTPService.generate_otp_code()
        
        # Set expiration time (5 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=5)
        
        # Create OTP record in database
        otp = OTP.objects.create(
            user=user,
            code=otp_code,
            expires_at=expires_at
        )
        
        # Send OTP via IPANEL
        success, response = OTPService.send_otp_via_ipanel(user.phone_number, otp_code)
        
        if success:
            return True, "OTP sent successfully"
        else:
            # Delete the OTP record if sending failed
            otp.delete()
            return False, f"Failed to send OTP: {response}"
    
    @staticmethod
    def verify_otp(user, otp_code):
        """
        Verify the OTP code for a user
        Returns (is_valid, message)
        """
        try:
            # Get the latest OTP for the user that hasn't been used and hasn't expired
            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            # Mark as used
            otp.is_used = True
            otp.save()
            
            return True, "OTP verified successfully"
        except OTP.DoesNotExist:
            return False, "Invalid or expired OTP code"