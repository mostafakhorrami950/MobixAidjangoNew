import os
import sys
import django
from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from subscriptions.services import UsageService

def debug_403_error(user_id, model_id=None):
    """
    Debug 403 Forbidden error for a user
    """
    try:
        # Get models dynamically
        User = get_user_model()
        AIModel = apps.get_model('ai_models', 'AIModel')
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        
        # 1. بررسی کاربر
        try:
            user = User.objects.get(id=user_id)
            print(f"✓ کاربر {user.name} ({user.phone_number}) یافت شد")
        except User.DoesNotExist:
            print(f"✗ کاربر با ID {user_id} یافت نشد")
            return
        
        # 2. بررسی اشتراک
        subscription = user.get_subscription_type()
        if subscription:
            print(f"✓ اشتراک فعال: {subscription.name}")
        else:
            print("✗ کاربر اشتراک فعال ندارد")
            return
        
        # 3. بررسی مدل
        if model_id:
            try:
                ai_model = AIModel.objects.get(model_id=model_id)
                print(f"✓ مدل {ai_model.name} یافت شد")
            except AIModel.DoesNotExist:
                print(f"✗ مدل با ID {model_id} یافت نشد")
                # Try to get any active text model
                ai_model = AIModel.objects.filter(is_active=True, model_type='text').first()
                if ai_model:
                    print(f"→ استفاده از مدل جایگزین: {ai_model.name}")
                else:
                    print("✗ هیچ مدل فعالی یافت نشد")
                    return
        else:
            # Get any active text model
            ai_model = AIModel.objects.filter(is_active=True, model_type='text').first()
            if ai_model:
                print(f"✓ استفاده از مدل: {ai_model.name}")
            else:
                print("✗ هیچ مدل فعالی یافت نشد")
                return
        
        # 4. بررسی دسترسی کاربر به مدل
        if user.has_access_to_model(ai_model):
            print(f"✓ کاربر دسترسی به مدل {ai_model.name} دارد")
        else:
            print(f"✗ کاربر دسترسی به مدل {ai_model.name} ندارد")
            print("  راه حل: مدل را به اشتراک کاربر اضافه کنید")
        
        # 5. بررسی توکن‌های مصرف شده
        total_paid_tokens, total_free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(user, subscription)
        total_tokens = total_paid_tokens + total_free_tokens
        print(f"\n--- آمار استفاده ---")
        print(f"کل توکن‌های مصرف شده: {total_tokens:,}")
        print(f"توکن‌های مدل رایگان: {total_free_tokens:,}")
        print(f"حداکثر توکن مجاز: {subscription.max_tokens:,}")
        print(f"حداکثر توکن رایگان: {subscription.max_tokens_free:,}")
        
        remaining_tokens = max(0, subscription.max_tokens - total_tokens)
        remaining_free_tokens = max(0, subscription.max_tokens_free - total_free_tokens)
        
        print(f"توکن‌های باقیمانده: {remaining_tokens:,}")
        print(f"توکن‌های رایگان باقیمانده: {remaining_free_tokens:,}")
        
        # 6. تست comprehensive check
        print(f"\n--- تست comprehensive check ---")
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription)
        
        if within_limit:
            print("✓ تست comprehensive check موفقیت‌آمیز")
            print("مشکل 403 احتمالاً مربوط به موارد دیگری است")
        else:
            print(f"✗ تست comprehensive check ناموفق")
            print(f"علت: {message}")
        
        # 7. بررسی محدودیت‌های زمانی
        print(f"\n--- محدودیت‌های اشتراک ---")
        print(f"محدودیت ساعتی: {subscription.hourly_max_tokens:,}")
        print(f"محدودیت 3 ساعتی: {subscription.three_hours_max_tokens:,}")
        print(f"محدودیت 12 ساعتی: {subscription.twelve_hours_max_tokens:,}")
        print(f"محدودیت روزانه: {subscription.daily_max_tokens:,}")
        print(f"محدودیت هفتگی: {subscription.weekly_max_tokens:,}")
        print(f"محدودیت ماهانه: {subscription.monthly_max_tokens:,}")
        
        # 8. بررسی usage records اخیر
        recent_usage = UserUsage.objects.filter(
            user=user, 
            subscription_type=subscription,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-created_at')[:5]
        
        print(f"\n--- استفاده‌های اخیر (24 ساعت گذشته) ---")
        if recent_usage:
            for usage in recent_usage:
                print(f"{usage.created_at.strftime('%H:%M:%S')}: {usage.messages_count} پیام, {usage.tokens_count} توکن")
        else:
            print("هیچ استفاده‌ای در 24 ساعت گذشته ثبت نشده")
        
        # 9. پیشنهاد راه‌حل
        print(f"\n--- پیشنهاد راه‌حل ---")
        if not within_limit:
            if "دسترسی به این مدل" in message:
                print("→ مدل را به اشتراک کاربر اضافه کنید")
            elif "حد مجاز" in message:
                if "رایگان" in message:
                    print("→ محدودیت‌های مدل رایگان را افزایش دهید")
                else:
                    print("→ محدودیت‌های استفاده را بازنشانی یا افزایش دهید")
            else:
                print("→ جزئیات خطا را بررسی کنید")
        else:
            print("→ مشکل احتمالاً در جای دیگری است. لاگ‌های سرور را بررسی کنید")
            
    except Exception as e:
        print(f"خطا در تشخیص مشکل: {str(e)}")

def reset_user_limits(user_id):
    """
    بازنشانی محدودیت‌های کاربر
    """
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
        subscription = user.get_subscription_type()
        
        if subscription:
            UsageService.reset_user_usage(user, subscription)
            UsageService.reset_chat_session_usage(user, subscription)
            print(f"✓ محدودیت‌های کاربر {user.name} بازنشانی شد")
        else:
            print("✗ کاربر اشتراک فعال ندارد")
    except Exception as e:
        print(f"✗ خطا در بازنشانی: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("استفاده: python debug_403_error.py USER_ID [MODEL_ID]")
        print("مثال: python debug_403_error.py 1")
        print("برای بازنشانی: python debug_403_error.py --reset USER_ID")
        sys.exit(1)
    
    if sys.argv[1] == '--reset' and len(sys.argv) > 2:
        reset_user_limits(int(sys.argv[2]))
    else:
        user_id = int(sys.argv[1])
        model_id = sys.argv[2] if len(sys.argv) > 2 else None
        debug_403_error(user_id, model_id)