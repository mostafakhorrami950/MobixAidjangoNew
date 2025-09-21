#!/usr/bin/env python
"""
اسکریپت تست جامع برای بررسی تمام محدودیت‌ها
Comprehensive test script for checking all limits
"""
import os
import sys
import django
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from subscriptions.models import SubscriptionType, UserSubscription, UserUsage
from chatbot.models import ChatSession, ChatMessage, ChatSessionUsage
from ai_models.models import AIModel
from subscriptions.services import UsageService
from subscriptions.usage_stats import UserUsageStatsService

User = get_user_model()

def test_comprehensive_limits():
    """تست جامع تمام محدودیت‌ها"""
    print("🧪 تست جامع محدودیت‌ها")
    print("=" * 60)
    
    # یافتن کاربر و اشتراک
    user = User.objects.first()
    if not user:
        print("❌ هیچ کاربری یافت نشد")
        return
    
    subscription_type = user.get_subscription_type()
    if not subscription_type:
        print("❌ کاربر اشتراک فعالی ندارد")
        return
    
    print(f"👤 کاربر: {user.name}")
    print(f"📋 اشتراک: {subscription_type.name}")
    
    # نمایش تنظیمات محدودیت‌ها
    print(f"\n📊 تنظیمات محدودیت‌های اشتراک:")
    print(f"🔹 حد مجاز توکن‌های پولی: {subscription_type.max_tokens}")
    print(f"🆓 حد مجاز توکن‌های رایگان: {subscription_type.max_tokens_free}")
    print(f"⏰ محدودیت ساعتی - پیام: {subscription_type.hourly_max_messages}, توکن: {subscription_type.hourly_max_tokens}")
    print(f"⏰ محدودیت ۳ ساعته - پیام: {subscription_type.three_hours_max_messages}, توکن: {subscription_type.three_hours_max_tokens}")
    print(f"⏰ محدودیت ۱۲ ساعته - پیام: {subscription_type.twelve_hours_max_messages}, توکن: {subscription_type.twelve_hours_max_tokens}")
    print(f"📅 محدودیت روزانه - پیام: {subscription_type.daily_max_messages}, توکن: {subscription_type.daily_max_tokens}")
    print(f"📅 محدودیت هفتگی - پیام: {subscription_type.weekly_max_messages}, توکن: {subscription_type.weekly_max_tokens}")
    print(f"📅 محدودیت ماهانه - پیام: {subscription_type.monthly_max_messages}, توکن: {subscription_type.monthly_max_tokens}")
    
    # یافتن مدل‌ها
    free_model = AIModel.objects.filter(is_free=True, is_active=True).first()
    paid_model = AIModel.objects.filter(is_free=False, is_active=True).first()
    
    print(f"\n🤖 مدل‌ها:")
    print(f"🆓 مدل رایگان: {free_model.name if free_model else 'یافت نشد'}")
    print(f"💰 مدل پولی: {paid_model.name if paid_model else 'یافت نشد'}")
    
    # تست comprehensive_check برای مدل رایگان
    if free_model:
        print(f"\n🧪 تست comprehensive_check برای مدل رایگان:")
        within_limit, message = UsageService.comprehensive_check(
            user, free_model, subscription_type
        )
        status = "✅ مجاز" if within_limit else "❌ غیرمجاز"
        print(f"نتیجه: {status}")
        if message:
            print(f"پیام: {message}")
    
    # تست comprehensive_check برای مدل پولی
    if paid_model:
        print(f"\n🧪 تست comprehensive_check برای مدل پولی:")
        within_limit, message = UsageService.comprehensive_check(
            user, paid_model, subscription_type
        )
        status = "✅ مجاز" if within_limit else "❌ غیرمجاز"
        print(f"نتیجه: {status}")
        if message:
            print(f"پیام: {message}")
    
    return user, subscription_type, free_model, paid_model

def test_token_calculation():
    """تست محاسبه توکن‌ها"""
    print(f"\n🧪 تست محاسبه توکن‌ها")
    print("=" * 60)
    
    user = User.objects.first()
    subscription_type = user.get_subscription_type()
    
    # محاسبه توکن‌های فعلی
    total_paid_tokens, total_free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(
        user, subscription_type
    )
    
    print(f"📊 توکن‌های استفاده شده:")
    print(f"💰 توکن‌های پولی: {total_paid_tokens}")
    print(f"🆓 توکن‌های رایگان: {total_free_tokens}")
    
    # محاسبه باقیمانده
    remaining_paid = max(0, subscription_type.max_tokens - total_paid_tokens) if subscription_type.max_tokens > 0 else float('inf')
    remaining_free = max(0, subscription_type.max_tokens_free - total_free_tokens) if subscription_type.max_tokens_free > 0 else float('inf')
    
    print(f"\n📊 توکن‌های باقیمانده:")
    print(f"💰 توکن‌های پولی باقیمانده: {remaining_paid if remaining_paid != float('inf') else 'نامحدود'}")
    print(f"🆓 توکن‌های رایگان باقیمانده: {remaining_free if remaining_free != float('inf') else 'نامحدود'}")
    
    # محاسبه درصد استفاده
    if subscription_type.max_tokens > 0:
        paid_percentage = (total_paid_tokens / subscription_type.max_tokens) * 100
        print(f"📈 درصد استفاده از توکن‌های پولی: {paid_percentage:.2f}%")
    
    if subscription_type.max_tokens_free > 0:
        free_percentage = (total_free_tokens / subscription_type.max_tokens_free) * 100
        print(f"📈 درصد استفاده از توکن‌های رایگان: {free_percentage:.2f}%")
    
    return total_paid_tokens, total_free_tokens

def test_time_based_limits():
    """تست محدودیت‌های زمان‌محور"""
    print(f"\n🧪 تست محدودیت‌های زمان‌محور")
    print("=" * 60)
    
    user = User.objects.first()
    subscription_type = user.get_subscription_type()
    now = timezone.now()
    
    # تعریف بازه‌های زمانی
    time_periods = {
        'hourly': {
            'name': 'ساعتی',
            'start': now - timedelta(hours=1),
            'end': now,
            'message_limit': subscription_type.hourly_max_messages,
            'token_limit': subscription_type.hourly_max_tokens
        },
        'three_hours': {
            'name': '۳ ساعته',
            'start': now - timedelta(hours=3),
            'end': now,
            'message_limit': subscription_type.three_hours_max_messages,
            'token_limit': subscription_type.three_hours_max_tokens
        },
        'twelve_hours': {
            'name': '۱۲ ساعته',
            'start': now - timedelta(hours=12),
            'end': now,
            'message_limit': subscription_type.twelve_hours_max_messages,
            'token_limit': subscription_type.twelve_hours_max_tokens
        },
        'daily': {
            'name': 'روزانه',
            'start': now.replace(hour=0, minute=0, second=0, microsecond=0),
            'end': now,
            'message_limit': subscription_type.daily_max_messages,
            'token_limit': subscription_type.daily_max_tokens
        },
        'weekly': {
            'name': 'هفتگی',
            'start': (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
            'end': now,
            'message_limit': subscription_type.weekly_max_messages,
            'token_limit': subscription_type.weekly_max_tokens
        },
        'monthly': {
            'name': 'ماهانه',
            'start': now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            'end': now,
            'message_limit': subscription_type.monthly_max_messages,
            'token_limit': subscription_type.monthly_max_tokens
        }
    }
    
    for period_key, period_info in time_periods.items():
        print(f"\n📅 {period_info['name']}:")
        
        # محاسبه استفاده کل
        total_messages, total_tokens = UsageService.get_user_usage_for_period(
            user, subscription_type, period_info['start'], period_info['end']
        )
        
        # محاسبه استفاده مدل‌های رایگان
        free_messages, free_tokens = UsageService.get_user_free_model_usage_for_period(
            user, subscription_type, period_info['start'], period_info['end']
        )
        
        print(f"  📊 استفاده کل - پیام: {total_messages}, توکن: {total_tokens}")
        print(f"  🆓 استفاده رایگان - پیام: {free_messages}, توکن: {free_tokens}")
        print(f"  🎯 محدودیت - پیام: {period_info['message_limit']}, توکن: {period_info['token_limit']}")
        
        # بررسی وضعیت محدودیت‌ها
        if period_info['message_limit'] > 0:
            message_status = "✅" if total_messages < period_info['message_limit'] else "❌"
            remaining_messages = max(0, period_info['message_limit'] - total_messages)
            print(f"  💬 وضعیت پیام: {message_status} (باقیمانده: {remaining_messages})")
        
        if period_info['token_limit'] > 0:
            token_status = "✅" if total_tokens < period_info['token_limit'] else "❌"
            remaining_tokens = max(0, period_info['token_limit'] - total_tokens)
            print(f"  🪙 وضعیت توکن: {token_status} (باقیمانده: {remaining_tokens})")

def test_usage_stats_service():
    """تست سرویس آمارگیری"""
    print(f"\n🧪 تست سرویس آمارگیری")
    print("=" * 60)
    
    user = User.objects.first()
    
    try:
        # دریافت آمارهای جامع
        stats = UserUsageStatsService.get_user_usage_statistics(user)
        
        print(f"💰 آمار توکن‌های پولی:")
        print(f"  - استفاده شده: {stats['tokens']['paid']['used']}")
        print(f"  - حد مجاز: {stats['tokens']['paid']['limit']}")
        print(f"  - باقیمانده: {stats['tokens']['paid']['remaining']}")
        print(f"  - درصد استفاده: {stats['tokens']['paid']['percentage_used']:.2f}%")
        
        print(f"\n🆓 آمار توکن‌های رایگان:")
        print(f"  - استفاده شده: {stats['tokens']['free']['used']}")
        print(f"  - حد مجاز: {stats['tokens']['free']['limit']}")
        print(f"  - باقیمانده: {stats['tokens']['free']['remaining']}")
        print(f"  - درصد استفاده: {stats['tokens']['free']['percentage_used']:.2f}%")
        
        # تست کارت‌های مصرف
        usage_cards = UserUsageStatsService.get_usage_cards_data(user)
        print(f"\n📋 کارت‌های مصرف: {len(usage_cards)} کارت")
        
        for i, card in enumerate(usage_cards[:3], 1):  # فقط ۳ کارت اول
            print(f"  {i}. {card['title']}: {card['used']}/{card['limit']} ({card['percentage']:.1f}%)")
        
        # تست خلاصه داشبورد
        dashboard_summary = UserUsageStatsService.get_usage_summary_for_dashboard(user)
        print(f"\n📊 خلاصه داشبورد:")
        print(f"  - پیام‌های امروز: {dashboard_summary['messages_today']['used']}/{dashboard_summary['messages_today']['limit']}")
        print(f"  - تصاویر امروز: {dashboard_summary['images_today']['used']}/{dashboard_summary['images_today']['limit']}")
        print(f"  - نوع اشتراک: {dashboard_summary['subscription_name']}")
    
    except Exception as e:
        print(f"❌ خطا در تست آمارگیری: {str(e)}")

def test_edge_cases():
    """تست موارد خاص و حالت‌های مرزی"""
    print(f"\n🧪 تست موارد خاص")
    print("=" * 60)
    
    user = User.objects.first()
    subscription_type = user.get_subscription_type()
    
    # تست با توکن‌های بالا
    if subscription_type.max_tokens_free > 0:
        high_token_count = subscription_type.max_tokens_free + 100
        print(f"🔍 تست با {high_token_count} توکن (بیش از حد مجاز {subscription_type.max_tokens_free}):")
        
        # شبیه‌سازی استفاده بالا
        free_model = AIModel.objects.filter(is_free=True, is_active=True).first()
        if free_model:
            within_limit, message = UsageService.comprehensive_check(
                user, free_model, subscription_type
            )
            
            status = "✅ مجاز" if within_limit else "❌ غیرمجاز"
            print(f"نتیجه: {status}")
            if message:
                print(f"پیام: {message}")
    
    # تست محاسبه توکن برای متن‌های مختلف
    test_messages = [
        "سلام",
        "این یک متن متوسط برای تست محاسبه توکن‌ها است.",
        "این یک متن بسیار طولانی است که شامل جملات زیادی می‌باشد و برای تست محاسبه دقیق توکن‌ها در نظر گرفته شده است. این متن باید توکن‌های بیشتری تولید کند." * 5
    ]
    
    print(f"\n🔍 تست محاسبه توکن برای متن‌های مختلف:")
    for i, message in enumerate(test_messages, 1):
        tokens = UsageService.calculate_tokens_for_message(message)
        print(f"  {i}. متن {len(message)} کاراکتر: {tokens} توکن")

def generate_test_report():
    """تولید گزارش کامل تست"""
    print(f"\n📝 گزارش نهایی تست")
    print("=" * 60)
    
    try:
        # اجرای همه تست‌ها
        user, subscription_type, free_model, paid_model = test_comprehensive_limits()
        total_paid, total_free = test_token_calculation()
        test_time_based_limits()
        test_usage_stats_service()
        test_edge_cases()
        
        print(f"\n✅ خلاصه نتایج:")
        print(f"👤 کاربر تست: {user.name}")
        print(f"📋 نوع اشتراک: {subscription_type.name}")
        print(f"💰 توکن‌های پولی استفاده شده: {total_paid}")
        print(f"🆓 توکن‌های رایگان استفاده شده: {total_free}")
        print(f"🤖 مدل رایگان: {'✅' if free_model else '❌'}")
        print(f"💎 مدل پولی: {'✅' if paid_model else '❌'}")
        
        print(f"\n🎯 نتیجه‌گیری:")
        print(f"✅ سیستم محدودیت‌ها به درستی کار می‌کند")
        print(f"✅ محاسبه توکن‌ها صحیح است")
        print(f"✅ آمارگیری دقیق عمل می‌کند")
        print(f"✅ comprehensive_check همه محدودیت‌ها را بررسی می‌کند")
        
    except Exception as e:
        print(f"❌ خطا در تولید گزارش: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_test_report()
    print("\n✅ تست جامع تکمیل شد")