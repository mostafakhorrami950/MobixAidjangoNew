# راهنمای رفع خطای 403 Forbidden در ارسال پیام

## دلایل احتمالی خطای 403

خطای 403 Forbidden هنگام ارسال پیام به chatbot معمولاً به دلیل محدودیت‌های اشتراک و استفاده رخ می‌دهد.

### 1. مشکلات اشتراک
- اشتراک کاربر منقضی شده است
- اشتراک غیرفعال است  
- کاربر دسترسی لازم به مدل انتخابی را ندارد

### 2. محدودیت‌های استفاده
- **محدودیت کل توکن**: کاربر به حد مجاز کل توکن‌های مصرفی رسیده
- **محدودیت‌های زمانی**: 
  - ساعتی (hourly_max_tokens)
  - 3 ساعتی (three_hours_max_tokens)  
  - 12 ساعتی (twelve_hours_max_tokens)
  - روزانه (daily_max_tokens)
  - هفتگی (weekly_max_tokens)
  - ماهانه (monthly_max_tokens)
- **محدودیت مدل‌های رایگان**: برای مدل‌های رایگان محدودیت جداگانه

## بررسی و رفع مشکل

### 1. بررسی وضعیت اشتراک کاربر
```python
# در Django shell یا مدیریت
python manage.py shell

from accounts.models import User
user = User.objects.get(id=USER_ID)  # شماره کاربر را جایگزین کنید

# بررسی اشتراک
subscription = user.get_subscription_type()
print(f"اشتراک فعلی: {subscription}")

if subscription:
    subscription_info = user.get_subscription_info()
    print(f"وضعیت اشتراک: {subscription_info}")
else:
    print("کاربر اشتراک فعال ندارد")
```

### 2. بررسی محدودیت‌های استفاده
```python
from subscriptions.services import UsageService

# بررسی توکن‌های مصرف شده
total_tokens, free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(user, subscription)
print(f"کل توکن‌های مصرف شده: {total_tokens}")
print(f"توکن‌های مدل رایگان: {free_tokens}")
print(f"حداکثر توکن مجاز: {subscription.max_tokens}")
```

### 3. بررسی comprehensive check
```python
from ai_models.models import AIModel

# مدل مورد استفاده را پیدا کنید
ai_model = AIModel.objects.get(model_id='MODEL_ID')  # model_id را جایگزین کنید

# تست comprehensive check
within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription)
print(f"نتیجه بررسی: {within_limit}")
print(f"پیام: {message}")
```

## راه‌حل‌های عملی

### 1. بازنشانی محدودیت‌های استفاده
```python
# بازنشانی usage counters
UsageService.reset_user_usage(user, subscription)
UsageService.reset_chat_session_usage(user, subscription)
print("محدودیت‌های استفاده بازنشانی شد")
```

### 2. تمدید یا ارتقاء اشتراک
```python
from subscriptions.models import UserSubscription, SubscriptionType
from django.utils import timezone
from datetime import timedelta

# تمدید اشتراک فعلی
if subscription:
    user_sub = UserSubscription.objects.get(user=user, subscription_type=subscription)
    user_sub.end_date = timezone.now() + timedelta(days=30)  # تمدید 30 روزه
    user_sub.save()
    print("اشتراک تمدید شد")

# یا ارتقاء به اشتراک جدید
new_subscription = SubscriptionType.objects.get(name='Premium')  # نام اشتراک مطلوب
UserSubscription.objects.update_or_create(
    user=user,
    defaults={
        'subscription_type': new_subscription,
        'is_active': True,
        'start_date': timezone.now(),
        'end_date': timezone.now() + timedelta(days=new_subscription.duration_days)
    }
)
print("اشتراک ارتقاء یافت")
```

### 3. افزایش محدودیت‌های اشتراک
```python
# افزایش حد مجاز توکن‌ها
if subscription:
    subscription.max_tokens = 2000000  # 2 میلیون توکن
    subscription.max_tokens_free = 100000  # 100 هزار توکن رایگان
    
    # افزایش محدودیت‌های زمانی
    subscription.daily_max_tokens = 50000
    subscription.weekly_max_tokens = 300000
    subscription.monthly_max_tokens = 1000000
    
    subscription.save()
    print("محدودیت‌های اشتراک افزایش یافت")
```

### 4. بررسی دسترسی کاربر به مدل
```python
# بررسی دسترسی به مدل
has_access = user.has_access_to_model(ai_model)
print(f"دسترسی به مدل {ai_model.name}: {has_access}")

if not has_access:
    # اضافه کردن مدل به اشتراک
    from ai_models.models import ModelSubscription
    model_sub, created = ModelSubscription.objects.get_or_create(ai_model=ai_model)
    model_sub.subscription_types.add(subscription)
    print(f"مدل {ai_model.name} به اشتراک {subscription.name} اضافه شد")
```

## نکات مهم

1. **لاگ‌ها را بررسی کنید**: در فایل `logs/` پیام‌های دقیق خطا موجود است
2. **مدل‌های رایگان**: حتی برای مدل‌های رایگان محدودیت وجود دارد
3. **محدودیت‌های زمانی**: محدودیت‌ها در بازه‌های زمانی مختلف اعمال می‌شود
4. **بازنشانی دوره‌ای**: محدودیت‌ها به صورت خودکار در ابتدای هر دوره بازنشانی نمی‌شود

## کمک اضافی

اگر مشکل همچنان ادامه دارد:

1. فایل `test_comprehensive_check.py` را اجرا کنید:
```bash
python test_comprehensive_check.py
```

2. command مدیریتی برای بررسی اشتراک‌های منقضی:
```bash
python manage.py check_expired_subscriptions
```

3. مراجعه به مستندات `COMPREHENSIVE_USAGE_CHECKING.md` برای اطلاعات بیشتر