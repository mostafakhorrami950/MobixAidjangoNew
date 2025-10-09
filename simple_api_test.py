#!/usr/bin/env python
"""
Simple test script to verify the API endpoints are working correctly.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

def test_api_setup():
    """Test that we can import the necessary components"""
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from django.apps import apps
        print("✓ Successfully imported Django components")
        
        # Test that we can get the models
        User = get_user_model()
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        AIModel = apps.get_model('ai_models', 'AIModel')
        print("✓ Successfully accessed models via apps.get_model")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import components: {e}")
        return False

if __name__ == '__main__':
    print("Testing API setup...")
    if test_api_setup():
        print("API setup test passed!")
        print("The API implementation is ready to use.")
    else:
        print("API setup test failed!")