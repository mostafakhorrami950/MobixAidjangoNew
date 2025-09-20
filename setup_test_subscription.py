#!/usr/bin/env python
"""
اسکریپت برای ایجاد اشتراک پایه و تست
"""
import os
import sys
import django
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionType, UserSubscription
from django.utils import timezone

User = get_user_model()

def setup_basic_subscription():
    """ایجاد اشتراک Basic اگر وجود ندارد"""
    print("🔧 تنظیم اشتراک Basic")
    
    # ایجاد یا دریافت اشتراک Basic
    basic_subscription, created = SubscriptionType.objects.get_or_create(
        name='Basic',
        defaults={
            'description': 'اشتراک رایگان پایه',
            'price': Decimal('0.00'),
            'duration_days': 365,  # یک سال
            'sku': 'basic_free',
            'max_tokens': 50000,  # 50K توکن پولی
            'max_tokens_free': 10000,  # 10K توکن رایگان
            'hourly_max_messages': 10,
            'hourly_max_tokens': 5000,
            'daily_max_messages': 50,
            'daily_max_tokens': 20000,
            'monthly_free_model_messages': 200,
            'monthly_free_model_tokens': 10000,
            'is_active': True
        }
    )
    
    if created:
        print("✅ اشتراک Basic ایجاد شد")
    else:
        print("📋 اشتراک Basic قبلاً موجود بود")
    
    print(f"🎯 حد مجاز توکن‌های رایگان: {basic_subscription.max_tokens_free}")
    print(f"💰 حد مجاز توکن‌های پولی: {basic_subscription.max_tokens}")
    
    return basic_subscription

def assign_subscription_to_user():
    """تخصیص اشتراک به کاربر"""
    print("\n👤 تخصیص اشتراک به کاربر")
    
    # یافتن کاربر
    user = User.objects.first()
    if not user:
        print("❌ هیچ کاربری یافت نشد")
        return None
    
    print(f"📋 کاربر: {user.name}")
    
    # دریافت اشتراک Basic
    try:
        basic_subscription = SubscriptionType.objects.get(name='Basic')
    except SubscriptionType.DoesNotExist:
        print("❌ اشتراک Basic یافت نشد")
        return None
    
    # ایجاد یا به‌روزرسانی اشتراک کاربر
    user_subscription, created = UserSubscription.objects.get_or_create(
        user=user,
        defaults={
            'subscription_type': basic_subscription,
            'is_active': True,
            'start_date': timezone.now()
        }
    )
    
    if not created:
        # اگر اشتراک قبلاً موجود بود، آن را به‌روزرسانی کنیم
        user_subscription.subscription_type = basic_subscription
        user_subscription.is_active = True
        user_subscription.start_date = timezone.now()
        user_subscription.save()
        print("🔄 اشتراک کاربر به‌روزرسانی شد")
    else:
        print("✅ اشتراک جدید برای کاربر ایجاد شد")
    
    return user_subscription

if __name__ == "__main__":
    setup_basic_subscription()
    assign_subscription_to_user()
    print("\n✅ تنظیمات تکمیل شد")