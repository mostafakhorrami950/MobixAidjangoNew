"""
سرویس مدیریت اشتراک‌ها و تخصیص خودکار پلن‌های پیش‌فرض
"""
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Tuple

from .models import DefaultSubscriptionSettings, SubscriptionType, UserSubscription
from accounts.models import User

logger = logging.getLogger(__name__)


class SubscriptionManager:
    """مدیر اشتراک‌ها و تخصیص خودکار پلن‌های پیش‌فرض"""
    
    @classmethod
    def assign_default_to_new_user(cls, user: User) -> Optional[UserSubscription]:
        """
        تخصیص پلن پیش‌فرض به کاربر جدید
        
        Args:
            user: کاربر جدید
            
        Returns:
            UserSubscription یا None در صورت خطا
        """
        try:
            # بررسی اینکه کاربر قبلاً اشتراک ندارد
            if hasattr(user, 'subscription') and user.subscription:
                logger.info(f"کاربر {user.phone_number} قبلاً اشتراک دارد")
                return user.subscription
            
            # دریافت پلن پیش‌فرض کاربران جدید
            default_plan = DefaultSubscriptionSettings.get_new_user_default()
            if not default_plan:
                logger.error("پلن پیش‌فرض کاربران جدید یافت نشد")
                return None
            
            # ایجاد اشتراک جدید
            subscription = UserSubscription.objects.create(
                user=user,
                subscription_type=default_plan,
                is_active=True,
                start_date=timezone.now(),
                end_date=None if default_plan.price == 0 else None
            )
            
            logger.info(f"پلن {default_plan.name} به کاربر جدید {user.phone_number} تخصیص داده شد")
            return subscription
            
        except Exception as e:
            logger.error(f"خطا در تخصیص پلن پیش‌فرض به کاربر {user.phone_number}: {str(e)}")
            return None
    
    @classmethod
    def handle_expired_subscription(cls, user: User) -> Tuple[bool, Optional[UserSubscription]]:
        """
        مدیریت اشتراک منقضی شده و تخصیص پلن fallback
        
        Args:
            user: کاربر با اشتراک منقضی شده
            
        Returns:
            (success: bool, new_subscription: UserSubscription یا None)
        """
        try:
            with transaction.atomic():
                # دریافت اشتراک فعلی
                current_subscription = user.subscription
                if not current_subscription:
                    logger.warning(f"کاربر {user.phone_number} اشتراک فعلی ندارد")
                    return False, None
                
                # بررسی انقضا
                if (current_subscription.end_date and 
                    current_subscription.end_date <= timezone.now() and 
                    current_subscription.is_active):
                    
                    # غیرفعال کردن اشتراک منقضی شده
                    current_subscription.is_active = False
                    current_subscription.save()
                    
                    logger.info(f"اشتراک {current_subscription.subscription_type.name} کاربر {user.phone_number} غیرفعال شد")
                    
                    # دریافت پلن fallback
                    fallback_plan = DefaultSubscriptionSettings.get_expired_fallback()
                    if not fallback_plan:
                        logger.error("پلن fallback یافت نشد")
                        return False, None
                    
                    # ایجاد اشتراک جدید
                    new_subscription = UserSubscription.objects.create(
                        user=user,
                        subscription_type=fallback_plan,
                        is_active=True,
                        start_date=timezone.now(),
                        end_date=None if fallback_plan.price == 0 else None
                    )
                    
                    logger.info(f"پلن fallback {fallback_plan.name} به کاربر {user.phone_number} تخصیص داده شد")
                    return True, new_subscription
                
                return False, current_subscription
                
        except Exception as e:
            logger.error(f"خطا در مدیریت انقضای اشتراک کاربر {user.phone_number}: {str(e)}")
            return False, None
    
    @classmethod
    def check_and_handle_expired_subscriptions(cls) -> Tuple[int, int]:
        """
        بررسی و مدیریت تمام اشتراک‌های منقضی شده
        
        Returns:
            (تعداد اشتراک‌های بررسی شده, تعداد اشتراک‌های پردازش شده)
        """
        try:
            # دریافت تمام اشتراک‌های فعال که منقضی شده‌اند
            expired_subscriptions = UserSubscription.objects.filter(
                is_active=True,
                end_date__lte=timezone.now()
            ).select_related('user', 'subscription_type')
            
            total_checked = expired_subscriptions.count()
            processed_count = 0
            
            logger.info(f"شروع بررسی {total_checked} اشتراک منقضی شده")
            
            for subscription in expired_subscriptions:
                success, new_sub = cls.handle_expired_subscription(subscription.user)
                if success:
                    processed_count += 1
            
            logger.info(f"پایان بررسی: {processed_count}/{total_checked} اشتراک پردازش شد")
            return total_checked, processed_count
            
        except Exception as e:
            logger.error(f"خطا در بررسی اشتراک‌های منقضی شده: {str(e)}")
            return 0, 0
    
    @classmethod
    def get_users_without_subscription(cls) -> List[User]:
        """
        دریافت کاربرانی که اشتراک ندارند
        
        Returns:
            لیست کاربران بدون اشتراک
        """
        try:
            return User.objects.filter(subscription__isnull=True)
        except Exception as e:
            logger.error(f"خطا در دریافت کاربران بدون اشتراک: {str(e)}")
            return []
    
    @classmethod
    def assign_default_to_users_without_subscription(cls) -> Tuple[int, int]:
        """
        تخصیص پلن پیش‌فرض به کاربرانی که اشتراک ندارند
        
        Returns:
            (تعداد کاربران بدون اشتراک, تعداد تخصیص‌های موفق)
        """
        try:
            users_without_subscription = cls.get_users_without_subscription()
            total_users = len(users_without_subscription)
            success_count = 0
            
            logger.info(f"شروع تخصیص پلن پیش‌فرض به {total_users} کاربر")
            
            for user in users_without_subscription:
                subscription = cls.assign_default_to_new_user(user)
                if subscription:
                    success_count += 1
            
            logger.info(f"پایان تخصیص: {success_count}/{total_users} تخصیص موفق")
            return total_users, success_count
            
        except Exception as e:
            logger.error(f"خطا در تخصیص پلن پیش‌فرض به کاربران: {str(e)}")
            return 0, 0
    
    @classmethod
    def get_subscription_statistics(cls) -> dict:
        """
        دریافت آمار اشتراک‌ها
        
        Returns:
            دیکشنری حاوی آمار اشتراک‌ها
        """
        try:
            stats = {
                'total_users': User.objects.count(),
                'users_with_subscription': User.objects.filter(subscription__isnull=False).count(),
                'users_without_subscription': User.objects.filter(subscription__isnull=True).count(),
                'active_subscriptions': UserSubscription.objects.filter(is_active=True).count(),
                'expired_subscriptions': UserSubscription.objects.filter(
                    is_active=True,
                    end_date__lte=timezone.now()
                ).count(),
                'subscription_types': {}
            }
            
            # آمار بر اساس نوع اشتراک
            for sub_type in SubscriptionType.objects.all():
                count = UserSubscription.objects.filter(
                    subscription_type=sub_type,
                    is_active=True
                ).count()
                stats['subscription_types'][sub_type.name] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"خطا در دریافت آمار اشتراک‌ها: {str(e)}")
            return {}
    
    @classmethod
    def validate_default_settings(cls) -> List[str]:
        """
        اعتبارسنجی تنظیمات پیش‌فرض
        
        Returns:
            لیست پیام‌های خطا (خالی در صورت عدم خطا)
        """
        errors = []
        
        try:
            # بررسی وجود تنظیم پیش‌فرض کاربران جدید
            new_user_setting = DefaultSubscriptionSettings.objects.filter(
                setting_type='new_user_default',
                is_active=True
            ).first()
            
            if not new_user_setting:
                errors.append("تنظیم پیش‌فرض کاربران جدید فعال یافت نشد")
            elif not new_user_setting.subscription_type.is_active:
                errors.append(f"پلن {new_user_setting.subscription_type.name} برای کاربران جدید غیرفعال است")
            
            # بررسی وجود تنظیم fallback
            fallback_setting = DefaultSubscriptionSettings.objects.filter(
                setting_type='expired_fallback',
                is_active=True
            ).first()
            
            if not fallback_setting:
                errors.append("تنظیم fallback فعال یافت نشد")
            elif not fallback_setting.subscription_type.is_active:
                errors.append(f"پلن {fallback_setting.subscription_type.name} برای fallback غیرفعال است")
            
            return errors
            
        except Exception as e:
            logger.error(f"خطا در اعتبارسنجی تنظیمات: {str(e)}")
            return [f"خطا در اعتبارسنجی: {str(e)}"]