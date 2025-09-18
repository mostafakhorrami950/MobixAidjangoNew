#!/usr/bin/env python
"""
Script to clear Django static cache
"""
import os
import sys
import shutil

# Get the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# Static files directory
static_root = os.path.join(project_dir, 'staticfiles')

# Clear the staticfiles directory if it exists
if os.path.exists(static_root):
    try:
        shutil.rmtree(static_root)
        print(f"✅ Successfully cleared static cache directory: {static_root}")
    except Exception as e:
        print(f"❌ Error clearing static cache: {str(e)}")
else:
    print("ℹ️ Static cache directory does not exist, nothing to clear")

print("\n🔄 Now run 'python manage.py collectstatic --noinput' to regenerate static files")