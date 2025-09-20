#!/usr/bin/env python
"""
اسکریپت تست برای بررسی محاسبه توکن‌های رایگان
Test script to verify free token calculation
"""
import os
import sys
import django
from decimal import Decimal

# اضافه کردن پروژه به مسیر Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تنظیم Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionType, UserSubscription, UserUsage
from chatbot.models import ChatSession, ChatMessage, ChatSessionUsage
from ai_models.models import AIModel
from subscriptions.services import UsageService
from subscriptions.usage_stats import UserUsageStatsService

User = get_user_model()

def test_free_token_calculation():
    """تست محاسبه توکن‌های رایگان"""
    print("🧪 شروع تست محاسبه توکن‌های رایگان")
    print("=" * 50)
    
    # یافتن یک کاربر تستی
    try:
        test_user = User.objects.first()
        if not test_user:
            print("❌ هیچ کاربری در دیتابیس پیدا نشد")
            return
        
        print(f"👤 کاربر تست: {test_user.name} ({test_user.phone_number})")
        
        # یافتن نوع اشتراک کاربر
        subscription_type = test_user.get_subscription_type()
        if not subscription_type:
            print("❌ کاربر اشتراک فعالی ندارد")
            return
        
        print(f"📋 نوع اشتراک: {subscription_type.name}")
        print(f"🎯 حد مجاز توکن‌های رایگان: {subscription_type.max_tokens_free}")
        print(f"💰 حد مجاز توکن‌های پولی: {subscription_type.max_tokens}")
        
    except Exception as e:
        print(f"❌ خطا در یافتن کاربر: {str(e)}")
        return
    
    print("\n" + "=" * 50)
    print("📊 آمارهای فعلی توکن‌ها")
    print("=" * 50)
    
    # محاسبه توکن‌های استفاده شده از ChatSessionUsage
    try:
        total_paid_tokens, total_free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(
            test_user, subscription_type
        )
        print(f"🔹 مجموع توکن‌های پولی (از ChatSessionUsage): {total_paid_tokens}")
        print(f"🆓 مجموع توکن‌های رایگان (از ChatSessionUsage): {total_free_tokens}")
        
        # محاسبه توکن‌های باقیمانده
        if subscription_type.max_tokens_free > 0:
            remaining_free_tokens = max(0, subscription_type.max_tokens_free - total_free_tokens)
            print(f"⏰ توکن‌های رایگان باقیمانده: {remaining_free_tokens}")
            free_usage_percentage = (total_free_tokens / subscription_type.max_tokens_free) * 100
            print(f"📈 درصد استفاده از توکن‌های رایگان: {free_usage_percentage:.2f}%")
        
        if subscription_type.max_tokens > 0:
            remaining_paid_tokens = max(0, subscription_type.max_tokens - total_paid_tokens)
            print(f"💎 توکن‌های پولی باقیمانده: {remaining_paid_tokens}")
            paid_usage_percentage = (total_paid_tokens / subscription_type.max_tokens) * 100
            print(f"📊 درصد استفاده از توکن‌های پولی: {paid_usage_percentage:.2f}%")
        
    except Exception as e:
        print(f"❌ خطا در محاسبه توکن‌ها: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🔍 بررسی ChatSessionUsage Records")
    print("=" * 50)
    
    # نمایش رکوردهای ChatSessionUsage
    try:
        session_usages = ChatSessionUsage.objects.filter(
            user=test_user,
            subscription_type=subscription_type
        )
        
        if session_usages.exists():
            print(f"📋 تعداد رکوردهای ChatSessionUsage: {session_usages.count()}")
            
            for i, usage in enumerate(session_usages[:5], 1):  # فقط 5 رکورد اول
                model_type = "رایگان" if usage.is_free_model else "پولی"
                print(f"  {i}. جلسه {usage.session.id} - نوع: {model_type}")
                print(f"     📊 توکن‌های پولی: {usage.tokens_count}")
                print(f"     🆓 توکن‌های رایگان: {usage.free_model_tokens_count}")
                print(f"     📅 ایجاد شده: {usage.created_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("📋 هیچ رکورد ChatSessionUsage یافت نشد")
    
    except Exception as e:
        print(f"❌ خطا در بررسی ChatSessionUsage: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🆓 بررسی مدل‌های رایگان")
    print("=" * 50)
    
    # نمایش مدل‌های رایگان
    try:
        free_models = AIModel.objects.filter(is_free=True, is_active=True)
        print(f"🔹 تعداد مدل‌های رایگان فعال: {free_models.count()}")
        
        for model in free_models:
            print(f"  • {model.name} ({model.model_id})")
            
            # شمارش پیام‌های استفاده شده برای هر مدل
            model_messages = ChatMessage.objects.filter(
                session__user=test_user,
                session__ai_model=model,
                message_type='assistant'
            ).count()
            
            if model_messages > 0:
                print(f"    📝 تعداد پیام‌های دستیار: {model_messages}")
    
    except Exception as e:
        print(f"❌ خطا در بررسی مدل‌های رایگان: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📈 آمارهای کامل (از UserUsageStatsService)")
    print("=" * 50)
    
    # استفاده از سرویس آمارگیری
    try:
        user_stats = UserUsageStatsService.get_user_usage_statistics(test_user)
        
        if 'tokens' in user_stats:
            tokens_stats = user_stats['tokens']
            
            print("💰 توکن‌های پولی:")
            print(f"  - استفاده شده: {tokens_stats['paid']['used']}")
            print(f"  - حد مجاز: {tokens_stats['paid']['limit']}")
            print(f"  - باقیمانده: {tokens_stats['paid']['remaining']}")
            print(f"  - درصد استفاده: {tokens_stats['paid']['percentage_used']:.2f}%")
            
            print("\n🆓 توکن‌های رایگان:")
            print(f"  - استفاده شده: {tokens_stats['free']['used']}")
            print(f"  - حد مجاز: {tokens_stats['free']['limit']}")
            print(f"  - باقیمانده: {tokens_stats['free']['remaining']}")
            print(f"  - درصد استفاده: {tokens_stats['free']['percentage_used']:.2f}%")
    
    except Exception as e:
        print(f"❌ خطا در دریافت آمارهای کامل: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ پایان تست")
    print("=" * 50)

def test_comprehensive_check():
    """تست بررسی جامع محدودیت‌ها"""
    print("\n🧪 شروع تست بررسی جامع محدودیت‌ها")
    print("=" * 50)
    
    try:
        test_user = User.objects.first()
        if not test_user:
            print("❌ هیچ کاربری در دیتابیس پیدا نشد")
            return
        
        subscription_type = test_user.get_subscription_type()
        if not subscription_type:
            print("❌ کاربر اشتراک فعالی ندارد")
            return
        
        # تست با مدل رایگان
        free_model = AIModel.objects.filter(is_free=True, is_active=True).first()
        if free_model:
            print(f"🆓 تست با مدل رایگان: {free_model.name}")
            
            within_limit, message = UsageService.comprehensive_check(
                test_user, free_model, subscription_type
            )
            
            status = "✅ مجاز" if within_limit else "❌ غیرمجاز"
            print(f"نتیجه: {status}")
            if message:
                print(f"پیام: {message}")
        
        # تست با مدل پولی
        paid_model = AIModel.objects.filter(is_free=False, is_active=True).first()
        if paid_model:
            print(f"\n💰 تست با مدل پولی: {paid_model.name}")
            
            within_limit, message = UsageService.comprehensive_check(
                test_user, paid_model, subscription_type
            )
            
            status = "✅ مجاز" if within_limit else "❌ غیرمجاز"
            print(f"نتیجه: {status}")
            if message:
                print(f"پیام: {message}")
    
    except Exception as e:
        print(f"❌ خطا در تست comprehensive_check: {str(e)}")

if __name__ == "__main__":
    test_free_token_calculation()
    test_comprehensive_check()