from django.utils import timezone
from datetime import timedelta
from .models import FileUploadSettings, FileUploadUsage, UploadedFile
from subscriptions.models import SubscriptionType

class FileUploadService:
    @staticmethod
    def get_file_upload_settings(subscription_type):
        """
        Get file upload settings for a subscription type
        """
        try:
            return FileUploadSettings.objects.get(
                subscription_type=subscription_type,
                is_active=True
            )
        except FileUploadSettings.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_file_upload_usage(user, subscription_type):
        """
        Get or create file upload usage record for a user and subscription type
        """
        now = timezone.now()
        
        # Calculate period start times
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get or create the usage record
        usage_record, created = FileUploadUsage.objects.get_or_create(
            user=user,
            subscription_type=subscription_type,
            defaults={
                'daily_files_count': 0,
                'weekly_files_count': 0,
                'monthly_files_count': 0,
                'session_files_count': 0,
                'daily_period_start': daily_start,
                'weekly_period_start': weekly_start,
                'monthly_period_start': monthly_start
            }
        )
        
        # Reset counters if periods have changed
        if not created:
            # Check and reset daily counter
            if usage_record.daily_period_start < daily_start:
                usage_record.daily_files_count = 0
                usage_record.daily_period_start = daily_start
            
            # Check and reset weekly counter
            if usage_record.weekly_period_start < weekly_start:
                usage_record.weekly_files_count = 0
                usage_record.weekly_period_start = weekly_start
            
            # Check and reset monthly counter
            if usage_record.monthly_period_start < monthly_start:
                usage_record.monthly_files_count = 0
                usage_record.monthly_period_start = monthly_start
            
            usage_record.save()
        
        return usage_record

    @staticmethod
    def check_file_upload_limit(user, subscription_type, session=None):
        """
        Check if user has exceeded file upload limits
        Returns (within_limit, message)
        """
        # Get file upload settings
        settings = FileUploadService.get_file_upload_settings(subscription_type)
        if not settings:
            return False, "تنظیمات آپلود فایل برای این اشتراک یافت نشد"
        
        # Get usage record
        usage_record = FileUploadService.get_or_create_file_upload_usage(user, subscription_type)
        
        # Check daily limit
        if settings.daily_file_limit > 0 and usage_record.daily_files_count >= settings.daily_file_limit:
            return False, f"شما به حد مجاز آپلود فایل روزانه ({settings.daily_file_limit} عدد) رسیده‌اید"
        
        # Check weekly limit
        if settings.weekly_file_limit > 0 and usage_record.weekly_files_count >= settings.weekly_file_limit:
            return False, f"شما به حد مجاز آپلود فایل هفتگی ({settings.weekly_file_limit} عدد) رسیده‌اید"
        
        # Check monthly limit
        if settings.monthly_file_limit > 0 and usage_record.monthly_files_count >= settings.monthly_file_limit:
            return False, f"شما به حد مجاز آپلود فایل ماهانه ({settings.monthly_file_limit} عدد) رسیده‌اید"
        
        # Check per-session limit
        if settings.max_files_per_chat > 0 and usage_record.session_files_count >= settings.max_files_per_chat:
            return False, f"شما به حد مجاز آپلود فایل در این جلسه ({settings.max_files_per_chat} عدد) رسیده‌اید"
        
        return True, ""

    @staticmethod
    def increment_file_upload_usage(user, subscription_type, session=None):
        """
        Increment file upload usage counters
        """
        # Get usage record
        usage_record = FileUploadService.get_or_create_file_upload_usage(user, subscription_type)
        
        # Increment all counters
        usage_record.daily_files_count += 1
        usage_record.weekly_files_count += 1
        usage_record.monthly_files_count += 1
        usage_record.session_files_count += 1
        
        usage_record.save()

    @staticmethod
    def check_file_extension_allowed(subscription_type, file_extension):
        """
        Check if file extension is allowed for this subscription type
        """
        settings = FileUploadService.get_file_upload_settings(subscription_type)
        if not settings:
            return False
        
        # If no extensions are specified, allow all
        if not settings.allowed_extensions:
            return True
        
        allowed_extensions = settings.get_allowed_extensions_list()
        
        # If no extensions are specified in the list, allow all
        if not allowed_extensions:
            return True
        
        # Check if file extension is in allowed list
        return file_extension.lower().strip('.') in allowed_extensions

    @staticmethod
    def check_file_size_limit(subscription_type, file_size):
        """
        Check if file size is within limit for this subscription type
        """
        settings = FileUploadService.get_file_upload_settings(subscription_type)
        if not settings:
            return False, "تنظیمات آپلود فایل برای این اشتراک یافت نشد"
        
        # If max_file_size is 0, there's no limit
        if settings.max_file_size == 0:
            return True, ""
        
        # Check if file size is within limit
        if file_size > settings.max_file_size:
            # Convert bytes to MB for display
            max_size_mb = settings.max_file_size / (1024 * 1024)
            file_size_mb = file_size / (1024 * 1024)
            return False, f"حجم فایل ({file_size_mb:.2f} MB) بیشتر از حد مجاز ({max_size_mb:.2f} MB) است"
        
        return True, ""