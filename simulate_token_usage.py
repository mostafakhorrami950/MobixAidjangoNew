#!/usr/bin/env python
"""
اسکریپت شبیه‌سازی استفاده از توکن‌های رایگان
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionType, UserSubscription
from chatbot.models import ChatSession, ChatMessage, ChatSessionUsage, Chatbot
from ai_models.models import AIModel
from subscriptions.services import UsageService
from subscriptions.usage_stats import UserUsageStatsService

User = get_user_model()

def create_test_chat_session():
    """ایجاد جلسه چت تستی"""
    print("🔧 ایجاد جلسه چت تستی")
    
    user = User.objects.first()
    subscription_type = user.get_subscription_type()
    
    # یافتن مدل رایگان
    free_model = AIModel.objects.filter(is_free=True, is_active=True).first()
    if not free_model:
        print("❌ مدل رایگان یافت نشد")
        return None
    
    print(f"🤖 استفاده از مدل رایگان: {free_model.name}")
    
    # ایجاد جلسه چت
    session = ChatSession.objects.create(
        user=user,
        ai_model=free_model,
        title="تست محاسبه توکن‌های رایگان"
    )
    
    # شبیه‌سازی چند پیام
    messages_data = [
        ("user", "سلام! چطوری؟", 10),
        ("assistant", "سلام! من خوبم، ممنون که پرسیدی. شما چطورید؟", 25),
        ("user", "من هم خوبم. می‌تونی درباره هوش مصنوعی توضیح بدی؟", 30),
        ("assistant", "البته! هوش مصنوعی یکی از مهم‌ترین فناوری‌های قرن بیست و یکم است که تلاش می‌کند تا رفتار انسان‌ها را شبیه‌سازی کند...", 120),
        ("user", "جالب بود! ممنون", 15),
        ("assistant", "خواهش می‌کنم! اگر سوال دیگری داشتید، در خدمتم.", 35)
    ]
    
    total_free_tokens = 0
    
    for msg_type, content, tokens in messages_data:
        message = ChatMessage.objects.create(
            session=session,
            message_type=msg_type,
            content=content,
            tokens_count=tokens
        )
        
        if msg_type == 'assistant':
            total_free_tokens += tokens
            print(f"💬 پیام دستیار: {tokens} توکن")
    
    print(f"📊 مجموع توکن‌های پیام‌های دستیار: {total_free_tokens}")
    
    # ایجاد ChatSessionUsage برای این جلسه
    chat_session_usage = ChatSessionUsage.objects.create(
        session=session,
        user=user,
        subscription_type=subscription_type,
        tokens_count=0,  # توکن‌های پولی
        free_model_tokens_count=total_free_tokens,  # توکن‌های رایگان
        is_free_model=True
    )
    
    print(f"✅ ChatSessionUsage ایجاد شد: {total_free_tokens} توکن رایگان")
    
    return session, total_free_tokens

def test_token_limits():
    """تست محدودیت توکن‌ها"""
    print("\n🧪 تست محدودیت توکن‌های رایگان")
    print("=" * 50)
    
    user = User.objects.first()
    subscription_type = user.get_subscription_type()
    free_model = AIModel.objects.filter(is_free=True, is_active=True).first()
    
    print(f"👤 کاربر: {user.name}")
    print(f"📋 اشتراک: {subscription_type.name}")
    print(f"🎯 حد مجاز توکن‌های رایگان: {subscription_type.max_tokens_free}")
    
    # بررسی وضعیت فعلی
    total_paid_tokens, total_free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(
        user, subscription_type
    )
    
    print(f"🆓 توکن‌های رایگان استفاده شده: {total_free_tokens}")
    print(f"⏰ توکن‌های رایگان باقیمانده: {max(0, subscription_type.max_tokens_free - total_free_tokens)}")
    
    # تست comprehensive_check
    within_limit, message = UsageService.comprehensive_check(
        user, free_model, subscription_type
    )
    
    status = "✅ مجاز" if within_limit else "❌ غیرمجاز"
    print(f"\n🔍 نتیجه comprehensive_check: {status}")
    if message:
        print(f"📋 پیام: {message}")
    
    # شبیه‌سازی پر کردن توکن‌های رایگان
    print(f"\n🔄 شبیه‌سازی پر کردن توکن‌های رایگان...")
    
    # محاسبه توکن‌هایی که نیاز داریم تا به حد مجاز برسیم
    remaining_tokens = subscription_type.max_tokens_free - total_free_tokens
    if remaining_tokens > 100:  # اگر بیش از 100 توکن باقی مانده
        # اضافه کردن توکن‌هایی که تقریباً به حد مجاز برسیم
        tokens_to_add = remaining_tokens - 30  # 30 توکن کمتر از حد مجاز
        
        # ایجاد یک جلسه جدید با توکن‌های بیشتر
        new_session = ChatSession.objects.create(
            user=user,
            ai_model=free_model,
            title="تست نزدیک به حد مجاز"
        )
        
        ChatMessage.objects.create(
            session=new_session,
            message_type='assistant',
            content='پیام طولانی برای پر کردن توکن‌ها...' * 10,
            tokens_count=tokens_to_add
        )
        
        ChatSessionUsage.objects.create(
            session=new_session,
            user=user,
            subscription_type=subscription_type,
            tokens_count=0,
            free_model_tokens_count=tokens_to_add,
            is_free_model=True
        )
        
        print(f"✅ {tokens_to_add} توکن رایگان اضافه شد")
        
        # بررسی مجدد
        total_paid_tokens, total_free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(
            user, subscription_type
        )
        print(f"🆓 توکن‌های رایگان جدید: {total_free_tokens}")
        print(f"⏰ باقیمانده: {max(0, subscription_type.max_tokens_free - total_free_tokens)}")
        
        # تست مجدد comprehensive_check
        within_limit, message = UsageService.comprehensive_check(
            user, free_model, subscription_type
        )
        
        status = "✅ مجاز" if within_limit else "❌ غیرمجاز"
        print(f"\n🔍 نتیجه جدید comprehensive_check: {status}")
        if message:
            print(f"📋 پیام: {message}")

def show_detailed_stats():
    """نمایش آمارهای تفصیلی"""
    print("\n📈 آمارهای تفصیلی نهایی")
    print("=" * 50)
    
    user = User.objects.first()
    
    try:
        user_stats = UserUsageStatsService.get_user_usage_statistics(user)
        
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
            
            # بررسی هشدار
            if tokens_stats['free']['percentage_used'] > 80:
                print("\n⚠️ هشدار: بیش از 80% توکن‌های رایگان استفاده شده!")
            elif tokens_stats['free']['percentage_used'] > 90:
                print("\n🚨 خطر: بیش از 90% توکن‌های رایگان استفاده شده!")
    
    except Exception as e:
        print(f"❌ خطا در دریافت آمارها: {str(e)}")

if __name__ == "__main__":
    session, tokens_used = create_test_chat_session()
    test_token_limits()
    show_detailed_stats()
    print("\n✅ شبیه‌سازی تکمیل شد")