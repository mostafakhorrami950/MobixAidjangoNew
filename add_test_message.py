#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت برای افزودن پیام تست به جلسه
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

def add_test_message_to_session(session_id):
    """افزودن پیام تست به جلسه"""
    print(f"افزودن پیام تست به جلسه {session_id}...")
    
    try:
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        ChatMessage = apps.get_model('chatbot', 'ChatMessage')
        
        # دریافت جلسه
        session = ChatSession.objects.get(id=session_id)
        
        # بررسی آیا پیامی وجود دارد
        message_count = session.messages.filter(message_type='user').count()
        if message_count > 0:
            print("جلسه از قبل پیام دارد")
            return True
            
        # ایجاد پیام تست
        test_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content='پیام تست برای تولید عنوان',
            tokens_count=0,
            created_at=timezone.now()
        )
        
        print(f"پیام تست ایجاد شد: {test_message.content}")
        return True
        
    except apps.get_model('chatbot', 'ChatSession').DoesNotExist:
        print(f"جلسه با شناسه {session_id} یافت نشد")
        return False
    except Exception as e:
        print(f"خطا در ایجاد پیام تست: {str(e)}")
        return False

if __name__ == "__main__":
    # استفاده از شناسه جلسه از تست قبلی
    session_id = 137  # این شناسه را از خروجی تست قبلی بگیرید
    add_test_message_to_session(session_id)