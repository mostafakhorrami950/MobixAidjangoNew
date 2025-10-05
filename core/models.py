from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class TermsAndConditions(models.Model):
    title = models.CharField(max_length=200, default="شرایط و قوانین استفاده", verbose_name="عنوان")
    content = models.TextField(
        verbose_name="محتوای شرایط و قوانین",
        help_text="محتوای شرایط و قوانین استفاده از سرویس را وارد کنید",
        default="شرایط و قوانین استفاده از سرویس در اینجا قرار خواهد گرفت."
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    
    class Meta:
        verbose_name = "شرایط و قوانین"
        verbose_name_plural = "شرایط و قوانین"
        db_table = 'terms_and_conditions'
    
    def __str__(self):
        return str(self.title)
    
    @classmethod
    def get_active_terms(cls):
        """Get the active terms and conditions"""
        return cls.objects.filter(is_active=True).first()


class GlobalSettings(models.Model):
    """
    Global application settings that can be configured by admin
    """
    # File Upload Settings
    max_file_size_mb = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(1024)],
        help_text="Maximum file upload size in MB (1-1024 MB)"
    )
    
    max_files_per_message = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Maximum number of files per message (1-20)"
    )
    
    allowed_file_extensions = models.TextField(
        default="txt,pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,webp",
        help_text="Comma-separated list of allowed file extensions (without dots)"
    )
    
    # Security Settings
    session_timeout_hours = models.PositiveIntegerField(
        default=24,
        validators=[MinValueValidator(1), MaxValueValidator(168)],  # 1-168 hours (1 week)
        help_text="User session timeout in hours"
    )
    
    # Performance Settings
    messages_per_page = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(10), MaxValueValidator(200)],
        help_text="Number of messages to load per page (pagination)"
    )
    
    # API Rate Limits
    api_requests_per_minute = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text="Maximum API requests per minute per user"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Global Settings"
        verbose_name_plural = "Global Settings"
    
    def __str__(self):
        return f"Global Settings (Max File Size: {self.max_file_size_mb}MB)"
    
    def save(self, *args, **kwargs):
        # Ensure only one GlobalSettings instance exists
        if not self.pk and GlobalSettings.objects.exists():
            raise ValueError("Only one GlobalSettings instance is allowed")
        super().save(*args, **kwargs)
    
    def get_allowed_extensions_list(self):
        """Return allowed extensions as a list"""
        if self.allowed_file_extensions:
            return [ext.strip().lower() for ext in self.allowed_file_extensions.split(',')]
        return []
    
    def get_max_file_size_bytes(self):
        """Return max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    @classmethod
    def get_settings(cls):
        """Get the active global settings instance"""
        settings, created = cls.objects.get_or_create(
            is_active=True,
            defaults={
                'max_file_size_mb': 10,
                'max_files_per_message': 5,
                'allowed_file_extensions': 'txt,pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,webp',
                'session_timeout_hours': 24,
                'messages_per_page': 50,
                'api_requests_per_minute': 60,
            }
        )
        return settings


class AdvertisingBanner(models.Model):
    """
    Advertising banner model that can be managed through the admin panel
    """
    title = models.CharField(max_length=200, verbose_name="عنوان بنر")
    image = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True,
        verbose_name="تصویر بنر",
        help_text="تصویر بنر تبلیغاتی"
    )
    link = models.URLField(max_length=500, verbose_name="لینک", help_text="لینک مقصد بنر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    
    class Meta:
        verbose_name = "بنر تبلیغاتی"
        verbose_name_plural = "بنرهای تبلیغاتی"
        db_table = 'advertising_banners'
        ordering = ['-created_at']
    
    def __str__(self):
        return str(self.title)
    
    @classmethod
    def get_active_banners(cls):
        """Get all active banners"""
        return cls.objects.filter(is_active=True)
    
    @classmethod
    def get_random_active_banner(cls):
        """Get a random active banner"""
        active_banners = cls.objects.filter(is_active=True)
        if active_banners.exists():
            return active_banners.order_by('?').first()
        return None
