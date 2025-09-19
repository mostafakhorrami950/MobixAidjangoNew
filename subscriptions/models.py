from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from accounts.models import User

class SubscriptionType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_days = models.IntegerField(default=30, help_text="Subscription duration in days")
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit for the subscription")
    max_tokens = models.IntegerField(default=0, help_text="Maximum tokens allowed for this subscription (0 for unlimited)")
    max_tokens_free = models.IntegerField(default=0, help_text="Maximum free tokens allowed for this subscription (0 for unlimited)")
    
    # Usage limits for different time periods
    hourly_max_messages = models.IntegerField(default=0, help_text="Maximum messages per hour (0 for unlimited)")
    hourly_max_tokens = models.IntegerField(default=0, help_text="Maximum tokens per hour (0 for unlimited)")
    three_hours_max_messages = models.IntegerField(default=0, help_text="Maximum messages per 3 hours (0 for unlimited)")
    three_hours_max_tokens = models.IntegerField(default=0, help_text="Maximum tokens per 3 hours (0 for unlimited)")
    twelve_hours_max_messages = models.IntegerField(default=0, help_text="Maximum messages per 12 hours (0 for unlimited)")
    twelve_hours_max_tokens = models.IntegerField(default=0, help_text="Maximum tokens per 12 hours (0 for unlimited)")
    daily_max_messages = models.IntegerField(default=0, help_text="Maximum messages per day (0 for unlimited)")
    daily_max_tokens = models.IntegerField(default=0, help_text="Maximum tokens per day (0 for unlimited)")
    weekly_max_messages = models.IntegerField(default=0, help_text="Maximum messages per week (0 for unlimited)")
    weekly_max_tokens = models.IntegerField(default=0, help_text="Maximum tokens per week (0 for unlimited)")
    monthly_max_messages = models.IntegerField(default=0, help_text="Maximum messages per month (0 for unlimited)")
    monthly_max_tokens = models.IntegerField(default=0, help_text="Maximum tokens per month (0 for unlimited)")
    
    # Free model usage limits
    monthly_free_model_messages = models.IntegerField(default=0, help_text="Maximum free model messages per month (0 for unlimited)")
    monthly_free_model_tokens = models.IntegerField(default=0, help_text="Maximum free model tokens per month (0 for unlimited)")
    
    # Image generation limits
    daily_image_generation_limit = models.IntegerField(default=10, help_text="Maximum images that can be generated per day (0 for unlimited)")
    weekly_image_generation_limit = models.IntegerField(default=50, help_text="Maximum images that can be generated per week (0 for unlimited)")
    monthly_image_generation_limit = models.IntegerField(default=200, help_text="Maximum images that can be generated per month (0 for unlimited)")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'subscription_types'

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.name} - {self.subscription_type.name}"
    
    class Meta:
        db_table = 'user_subscriptions'

class UserUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_records')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    messages_count = models.IntegerField(default=0)
    tokens_count = models.IntegerField(default=0)
    free_model_messages_count = models.IntegerField(default=0)
    free_model_tokens_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.subscription_type.name} - {self.created_at}"
    
    class Meta:
        db_table = 'user_usage'

class DiscountCode(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True, help_text="Discount code")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discount value (percentage or fixed amount)")
    subscription_types = models.ManyToManyField(SubscriptionType, blank=True, help_text="Subscription types this code applies to (leave blank for all)")
    max_uses = models.IntegerField(null=True, blank=True, help_text="Maximum total uses (leave blank for unlimited)")
    max_uses_per_user = models.IntegerField(default=1, help_text="Maximum uses per user")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiration date (leave blank for no expiration)")
    is_active = models.BooleanField(default=True, help_text="Is this discount code active?")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"
    
    class Meta:
        db_table = 'discount_codes'
        verbose_name = "Discount Code"
        verbose_name_plural = "Discount Codes"
    
    @property
    def is_expired(self):
        """Check if the discount code has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def uses_count(self):
        """Get the total number of times this code has been used"""
        return self.discount_uses.count()
    
    def is_valid_for_user(self, user):
        """Check if the discount code is valid for a specific user"""
        if not self.is_active:
            return False
        
        if self.is_expired:
            return False
        
        if self.max_uses and self.uses_count >= self.max_uses:
            return False
        
        # Check user usage limit
        user_uses = self.discount_uses.filter(user=user).count()
        if user_uses >= self.max_uses_per_user:
            return False
        
        return True
    
    def calculate_discount(self, amount):
        """Calculate the discount amount"""
        # Ensure amount is a Decimal
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        if self.discount_type == 'percentage':
            return amount * (self.discount_value / Decimal('100'))
        else:  # fixed
            # Don't allow discount to exceed the amount
            return min(self.discount_value, amount)

class DiscountUse(models.Model):
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.CASCADE, related_name='discount_uses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discount_uses')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.discount_code.code} used by {self.user.name}"
    
    class Meta:
        db_table = 'discount_uses'
        verbose_name = "Discount Use"
        verbose_name_plural = "Discount Uses"


class DefaultSubscriptionSettings(models.Model):
    """
    تنظیمات پلن‌های پیش‌فرض اشتراک
    این مدل برای مدیریت پلن‌هایی است که به صورت خودکار تخصیص داده می‌شوند
    """
    SETTING_TYPES = [
        ('new_user_default', 'پلن پیش‌فرض کاربران جدید'),
        ('expired_fallback', 'پلن پیش‌فرض پس از انقضا'),
    ]
    
    setting_type = models.CharField(
        max_length=20, 
        choices=SETTING_TYPES, 
        unique=True,
        verbose_name='نوع تنظیم',
        help_text='نوع تنظیم پیش‌فرض'
    )
    
    subscription_type = models.ForeignKey(
        SubscriptionType, 
        on_delete=models.CASCADE,
        verbose_name='پلن اشتراک',
        help_text='پلن اشتراکی که به عنوان پیش‌فرض تخصیص داده می‌شود'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
        help_text='آیا این تنظیم فعال است؟'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='توضیح',
        help_text='توضیح اختیاری در مورد این تنظیم'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'default_subscription_settings'
        verbose_name = 'تنظیمات پیش‌فرض اشتراک'
        verbose_name_plural = 'تنظیمات پیش‌فرض اشتراک'
        ordering = ['setting_type']
    
    def __str__(self):
        return f"{self.get_setting_type_display()}: {self.subscription_type.name}"
    
    def clean(self):
        """اعتبارسنجی داده‌ها"""
        # بررسی اینکه پلن انتخابی فعال باشد
        if self.subscription_type and not self.subscription_type.is_active:
            raise ValidationError({
                'subscription_type': 'پلن انتخابی باید فعال باشد.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_new_user_default(cls):
        """دریافت پلن پیش‌فرض کاربران جدید"""
        try:
            setting = cls.objects.get(setting_type='new_user_default', is_active=True)
            return setting.subscription_type
        except (cls.DoesNotExist, cls.MultipleObjectsReturned):
            # بازگشت به پلن Basic اگر تنظیم پیدا نشد
            try:
                return SubscriptionType.objects.get(name='Basic', is_active=True)
            except SubscriptionType.DoesNotExist:
                return None
    
    @classmethod
    def get_expired_fallback(cls):
        """دریافت پلن پیش‌فرض پس از انقضا"""
        try:
            setting = cls.objects.get(setting_type='expired_fallback', is_active=True)
            return setting.subscription_type
        except (cls.DoesNotExist, cls.MultipleObjectsReturned):
            # بازگشت به پلن Basic اگر تنظیم پیدا نشد
            try:
                return SubscriptionType.objects.get(name='Basic', is_active=True)
            except SubscriptionType.DoesNotExist:
                return None


class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('subscription_purchase', 'Subscription Purchase'),
        ('subscription_upgrade', 'Subscription Upgrade'),
        ('subscription_renewal', 'Subscription Renewal'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_transactions')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    
    # Financial details
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in Tomans")
    original_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original amount before discounts in Tomans")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Discount amount in Tomans")
    
    # Payment gateway details
    authority = models.CharField(max_length=100, unique=True, help_text="Payment authority from gateway")
    reference_id = models.CharField(max_length=100, null=True, blank=True, help_text="Reference ID from payment gateway")
    
    # Discount information
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.get_transaction_type_display()} - {self.amount} Tomans"
    
    class Meta:
        db_table = 'financial_transactions'
        verbose_name = "Financial Transaction"
        verbose_name_plural = "Financial Transactions"
        ordering = ['-created_at']
