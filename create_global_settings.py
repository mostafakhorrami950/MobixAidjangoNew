#!/usr/bin/env python
"""
Script to create default GlobalSettings instance
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobixAIdjango.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from core.models import GlobalSettings

def create_default_global_settings():
    """Create default global settings if none exist"""
    try:
        # Check if GlobalSettings already exists
        if GlobalSettings.objects.exists():
            print("GlobalSettings already exists. Current settings:")
            settings = GlobalSettings.get_settings()
            print(f"  Max file size: {settings.max_file_size_mb} MB")
            print(f"  Max files per message: {settings.max_files_per_message}")
            print(f"  Allowed extensions: {settings.allowed_file_extensions}")
            print(f"  Session timeout: {settings.session_timeout_hours} hours")
            print(f"  Messages per page: {settings.messages_per_page}")
            print(f"  API requests per minute: {settings.api_requests_per_minute}")
            return settings
        
        # Create default GlobalSettings
        settings = GlobalSettings.objects.create(
            max_file_size_mb=10,
            max_files_per_message=5,
            allowed_file_extensions="txt,pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,webp",
            session_timeout_hours=24,
            messages_per_page=50,
            api_requests_per_minute=60,
            is_active=True
        )
        
        print("Default GlobalSettings created successfully!")
        print(f"  Max file size: {settings.max_file_size_mb} MB")
        print(f"  Max files per message: {settings.max_files_per_message}")
        print(f"  Allowed extensions: {settings.allowed_file_extensions}")
        print(f"  Session timeout: {settings.session_timeout_hours} hours")
        print(f"  Messages per page: {settings.messages_per_page}")
        print(f"  API requests per minute: {settings.api_requests_per_minute}")
        
        return settings
        
    except Exception as e:
        print(f"Error creating GlobalSettings: {str(e)}")
        return None

if __name__ == "__main__":
    create_default_global_settings()