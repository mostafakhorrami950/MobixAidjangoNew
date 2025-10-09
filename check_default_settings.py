#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت برای بررسی تنظیمات پیش‌فرض چت
"""

import os
import sys
import django

# تنظیم مسیر پروژه
sys.path.append('c:\\Users\\10\\Projects\\mobixaidjangonew')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.apps import apps

# Get model using apps.get_model to avoid import issues
DefaultChatSettings = apps.get_model('chatbot', 'DefaultChatSettings')

def check_default_settings():
    """بررسی تنظیمات پیش‌فرض"""
    print("بررسی تنظیمات پیش‌فرض چت...")
    
    # بررسی تنظیمات فعال
    active_settings = DefaultChatSettings.objects.filter(is_active=True)
    print(f"تعداد تنظیمات فعال: {active_settings.count()}")
    
    if active_settings.exists():
        for setting in active_settings:
            print(f"- {setting.name}: {setting.default_chatbot.name} با مدل {setting.default_ai_model.name}")
    else:
        print("هیچ تنظیم فعالی یافت نشد")
        
        # بررسی تنظیمات غیرفعال
        inactive_settings = DefaultChatSettings.objects.filter(is_active=False)
        print(f"تعداد تنظیمات غیرفعال: {inactive_settings.count()}")
        
        if inactive_settings.exists():
            print("تنظیمات غیرفعال موجود:")
            for setting in inactive_settings:
                print(f"- {setting.name}: {setting.default_chatbot.name} با مدل {setting.default_ai_model.name}")

if __name__ == "__main__":
    check_default_settings()