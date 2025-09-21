#!/usr/bin/env python
"""
Deployment script for MobixAI
This script prepares the application for production deployment
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def main():
    """Main deployment function"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
    
    try:
        # Setup Django
        django.setup()
        
        print("🚀 Starting MobixAI deployment preparation...")
        
        # Collect static files
        print("📦 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully!")
        
        # Run migrations
        print("🗄️  Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed!")
        
        # Create superuser if needed (optional)
        print("👤 Creating superuser (if needed)...")
        try:
            execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
            print("✅ Superuser created!")
        except:
            print("ℹ️  Superuser already exists or creation skipped")
        
        print("🎉 Deployment preparation completed successfully!")
        print("🔧 Make sure to set the following environment variables:")
        print("   - SECRET_KEY")
        print("   - DEBUG=False")
        print("   - DATABASE_URL (for PostgreSQL)")
        print("   - ALLOWED_HOSTS")
        print("   - OPENROUTER_API_KEY")
        print("   - ZARINPAL_MERCHANT_ID")
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()