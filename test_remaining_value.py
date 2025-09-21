import os
import django
from django.conf import settings

# تنظیم محیط جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from subscriptions.views import calculate_remaining_subscription_value
from subscriptions.models import SubscriptionType, UserSubscription
from django.utils import timezone
from datetime import timedelta

# دریافت مدل کاربر
User = get_user_model()

def test_remaining_value():
    # ایجاد یک کاربر تست
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(username='testuser', password='testpass123')
    
    # ایجاد یک نوع اشتراک تست
    try:
        subscription_type = SubscriptionType.objects.get(name='Test Subscription')
    except SubscriptionType.DoesNotExist:
        subscription_type = SubscriptionType.objects.create(
            name='Test Subscription',
            description='Test subscription for debugging',
            price=10000,  # 10,000 تومان
            duration_days=30,
            max_tokens=100000,
            is_active=True
        )
    
    # ایجاد اشتراک کاربر
    try:
        user_subscription = UserSubscription.objects.get(user=user, subscription_type=subscription_type)
    except UserSubscription.DoesNotExist:
        user_subscription = UserSubscription.objects.create(
            user=user,
            subscription_type=subscription_type,
            is_active=True,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
    
    # ایجاد یک درخواست تست
    factory = RequestFactory()
    request = factory.get('/subscriptions/calculate-remaining-value/')
    request.user = user
    
    # فراخوانی تابع
    response = calculate_remaining_subscription_value(request)
    
    # نمایش نتیجه
    print("Response status code:", response.status_code)
    print("Response content:", response.content.decode('utf-8'))

if __name__ == '__main__':
    test_remaining_value()