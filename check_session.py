#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت برای بررسی جزئیات جلسه
"""

import os
import sys
import django

# تنظیم مسیر پروژه
sys.path.append('c:\\Users\\10\\Projects\\mobixaidjangonew')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.apps import apps
from django.utils import timezone

def check_session_details(session_id):
    """بررسی جزئیات جلسه"""
    print(f"بررسی جزئیات جلسه {session_id}")
    print("=" * 50)
    
    try:
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        ChatMessage = apps.get_model('chatbot', 'ChatMessage')
        
        # دریافت جلسه
        session = ChatSession.objects.get(id=session_id)
        
        print(f"شناسه جلسه: {session.id}")
        print(f"عنوان جلسه: '{session.title}'")
        print(f"تولید خودکار عنوان: {session.auto_generate_title}")
        print(f"چت‌بات: {session.chatbot.name if session.chatbot else 'ندارد'}")
        print(f"مدل AI: {session.ai_model.name if session.ai_model else 'ندارد'}")
        print(f"تاریخ ایجاد: {session.created_at}")
        print(f"تاریخ به‌روزرسانی: {session.updated_at}")
        
        # بررسی پیام‌ها
        user_messages = session.messages.filter(message_type='user', disabled=False)
        print(f"\nتعداد پیام‌های کاربر: {user_messages.count()}")
        
        for i, message in enumerate(user_messages):
            print(f"  پیام {i+1}: '{message.content}' (تاریخ: {message.created_at})")
        
        # بررسی شرایط تولید عنوان
        print(f"\nبررسی شرایط تولید عنوان:")
        print(f"  auto_generate_title: {session.auto_generate_title}")
        print(f"  title: '{session.title}'")
        print(f"  title != 'چت جدید': {session.title != 'چت جدید' if session.title else 'False'}")
        print(f"  user_messages_count == 1: {user_messages.count() == 1}")
        
        should_generate = True
        if not session.auto_generate_title:
            should_generate = False
            print("  نتیجه: باید عنوان تولید شود؟ False (auto_generate_title=False)")
        elif session.title and session.title != 'چت جدید':
            should_generate = False
            print("  نتیجه: باید عنوان تولید شود؟ False (عنوان سفارشی تنظیم شده)")
        elif user_messages.count() != 1:
            should_generate = False
            print("  نتیجه: باید عنوان تولید شود؟ False (تعداد پیام‌ها 1 نیست)")
        else:
            print("  نتیجه: باید عنوان تولید شود؟ True")
            
        # بررسی اولین پیام
        first_message = session.get_first_user_message()
        if first_message:
            print(f"\nاولین پیام کاربر: '{first_message.content}'")
        else:
            print(f"\nاولین پیام کاربر: یافت نشد")
            
    except apps.get_model('chatbot', 'ChatSession').DoesNotExist:
        print(f"جلسه با شناسه {session_id} یافت نشد")
    except Exception as e:
        print(f"خطا در بررسی جلسه: {str(e)}")

if __name__ == "__main__":
    # استفاده از شناسه جلسه از تست قبلی
    session_id = 137
    check_session_details(session_id)