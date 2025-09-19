from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone

class CustomUserManager(UserManager):
    def create_user(self, phone_number, name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        if not name:
            raise ValueError('The Name must be set')
        
        user = self.model(phone_number=phone_number, name=name, **extra_fields)
        user.username = phone_number  # Set username to phone number
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, name, password, **extra_fields)

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} - {self.phone_number}"
    
    def save(self, *args, **kwargs):
        # Check if this is a new user
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # If this is a new user, assign them the default subscription
        if is_new:
            self.assign_default_subscription()
    
    def assign_default_subscription(self, subscription_type=None):
        """
        تخصیص پلن اشتراک پیش‌فرض به کاربر
        اگر subscription_type مشخص نشد، از تنظیمات پیش‌فرض استفاده می‌شود
        """
        from subscriptions.models import DefaultSubscriptionSettings, UserSubscription
        
        # بررسی اینکه کاربر قبلاً اشتراک نداشته باشد
        if hasattr(self, 'subscription') and self.subscription:
            return self.subscription
        
        # تعیین پلن اشتراک
        if subscription_type is None:
            subscription_type = DefaultSubscriptionSettings.get_new_user_default()
        
        if subscription_type:
            try:
                # ایجاد اشتراک برای کاربر
                user_subscription = UserSubscription.objects.create(
                    user=self,
                    subscription_type=subscription_type,
                    is_active=True,
                    start_date=timezone.now(),
                    # برای پلن‌های رایگان، end_date تنظیم نمی‌شود
                    end_date=None if subscription_type.price == 0 else None
                )
                return user_subscription
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"خطا در تخصیص اشتراک پیش‌فرض به کاربر {self.phone_number}: {str(e)}")
        
        return None
    
    def handle_subscription_expiry(self):
        """
        مدیریت انقضای اشتراک و تخصیص پلن پیش‌فرض جدید
        """
        from subscriptions.models import DefaultSubscriptionSettings, UserSubscription
        
        try:
            user_subscription = self.subscription
            if (user_subscription.end_date and 
                user_subscription.end_date < timezone.now() and 
                user_subscription.is_active):
                
                # غیرفعال کردن اشتراک منقضی‌شده
                user_subscription.is_active = False
                user_subscription.save()
                
                # تخصیص پلن fallback
                fallback_subscription = DefaultSubscriptionSettings.get_expired_fallback()
                if fallback_subscription:
                    UserSubscription.objects.create(
                        user=self,
                        subscription_type=fallback_subscription,
                        is_active=True,
                        start_date=timezone.now(),
                        end_date=None if fallback_subscription.price == 0 else None
                    )
                    
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"پلن fallback {fallback_subscription.name} به کاربر {self.phone_number} تخصیص داده شد")
                
                return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"خطا در مدیریت انقضای اشتراک برای کاربر {self.phone_number}: {str(e)}")
        
        return False
    
    def get_subscription_type(self):
        """
        Get the user's current subscription type
        """
        try:
            user_subscription = self.subscription
            if user_subscription.is_active:
                # Check if subscription has expired
                if user_subscription.end_date and user_subscription.end_date < timezone.now():
                    # Handle expiry and assign fallback
                    self.handle_subscription_expiry()
                    # Get the new subscription after expiry handling
                    try:
                        return self.subscription.subscription_type
                    except:
                        return None
                return user_subscription.subscription_type
        except:
            # If no subscription exists, assign default
            self.assign_default_subscription()
            try:
                return self.subscription.subscription_type
            except:
                pass
        return None
    
    def get_subscription_info(self):
        """
        Get detailed subscription information including expiration date and usage
        """
        try:
            user_subscription = self.subscription
            if user_subscription.is_active:
                # Check if subscription has expired
                if user_subscription.end_date and user_subscription.end_date < timezone.now():
                    # Handle expiry and assign fallback
                    self.handle_subscription_expiry()
                    # Get the new subscription after expiry handling
                    try:
                        return self.subscription
                    except:
                        return None
                return user_subscription
        except:
            # If no subscription exists, assign default
            self.assign_default_subscription()
            try:
                return self.subscription
            except:
                pass
        return None
    
    def has_access_to_model(self, ai_model):
        """
        Check if user has access to a specific AI model
        """
        # Free models are accessible to all registered users
        if ai_model.is_free:
            return True
            
        # Check if user has a subscription
        subscription_type = self.get_subscription_type()
        if not subscription_type:
            return False
            
        # Check if the model is available for this subscription type
        # The model can be accessed if it's linked to the user's subscription type through ModelSubscription
        try:
            # Check if there's a ModelSubscription that links this AI model to the user's subscription type
            from ai_models.models import ModelSubscription
            return ModelSubscription.objects.filter(
                ai_model=ai_model, 
                subscription_types=subscription_type
            ).exists()
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking model access: {str(e)}")
            return False