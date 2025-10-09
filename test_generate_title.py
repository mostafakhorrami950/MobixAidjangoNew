#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت برای تست اندپوینت تولید عنوان
"""

import requests
import json

# تنظیمات پایه
BASE_URL = "http://localhost:8000"

# اطلاعات کاربر تست
TEST_PHONE = "09987654321"
TEST_PASSWORD = "testpassword2"

def get_auth_token():
    """دریافت توکن احراز هویت"""
    url = f"{BASE_URL}/api-token-auth/"
    data = {
        "username": TEST_PHONE,
        "password": TEST_PASSWORD
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"خطا در دریافت توکن: {response.status_code} - {response.text}")
        return None

def test_generate_title(token, session_id):
    """تست اندپوینت تولید عنوان"""
    url = f"{BASE_URL}/api/chatbot/sessions/{session_id}/generate_title/"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    
    print(f"تست اندپوینت تولید عنوان برای جلسه {session_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ موفق: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return True
    else:
        print(f"✗ ناموفق: {response.text}")
        return False

def main():
    """تابع اصلی"""
    print("تست اندپوینت تولید عنوان")
    print("=" * 50)
    
    # دریافت توکن
    token = get_auth_token()
    if not token:
        print("عدم موفقیت در دریافت توکن")
        return
    
    # استفاده از شناسه جلسه از تست قبلی
    session_id = 137
    success = test_generate_title(token, session_id)
    
    if success:
        print("\n✓ اندپوینت تولید عنوان به درستی کار می‌کند")
    else:
        print("\n✗ اندپوینت تولید عنوان مشکل دارد")

if __name__ == "__main__":
    main()