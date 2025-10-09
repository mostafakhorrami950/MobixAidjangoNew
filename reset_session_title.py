#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت برای بازنشانی عنوان جلسه
"""

import os
import sys
import django

# تنظیم مسیر پروژه
sys.path.append('c:\\Users\\10\\Projects\\mobixaidjangonew')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.apps import apps

def reset_session_title(session_id):
    """بازنشانی عنوان جلسه"""
    print(f"بازنشانی عنوان جلسه {session_id}")
    print("=" * 50)
    
    try:
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        
        # دریافت جلسه
        session = ChatSession.objects.get(id=session_id)
        
        print(f"عنوان فعلی: '{session.title}'")
        
        # بازنشانی عنوان به "چت جدید"
        old_title = session.title
        session.title = 'چت جدید'
        session.save(update_fields=['title'])
        
        print(f"عنوان قبلی: '{old_title}'")
        print(f"عنوان جدید: '{session.title}'")
        print("✓ عنوان جلسه بازنشانی شد")
        
        return True
        
    except apps.get_model('chatbot', 'ChatSession').DoesNotExist:
        print(f"جلسه با شناسه {session_id} یافت نشد")
        return False
    except Exception as e:
        print(f"خطا در بازنشانی عنوان جلسه: {str(e)}")
        return False

if __name__ == "__main__":
    # استفاده از شناسه جلسه از تست قبلی
    session_id = 137
    reset_session_title(session_id)