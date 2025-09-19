from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import (SubscriptionType, UserSubscription, UserUsage, 
                     DiscountCode, DiscountUse, FinancialTransaction, DefaultSubscriptionSettings)

@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price', 'is_active')
        }),
        ('Subscription Details', {
            'fields': ('duration_days', 'sku', 'max_tokens', 'max_tokens_free')
        }),
        ('Usage Limits - Hourly', {
            'fields': ('hourly_max_messages', 'hourly_max_tokens'),
            'classes': ('collapse',)
        }),
        ('Usage Limits - 3 Hours', {
            'fields': ('three_hours_max_messages', 'three_hours_max_tokens'),
            'classes': ('collapse',)
        }),
        ('Usage Limits - 12 Hours', {
            'fields': ('twelve_hours_max_messages', 'twelve_hours_max_tokens'),
            'classes': ('collapse',)
        }),
        ('Usage Limits - Daily', {
            'fields': ('daily_max_messages', 'daily_max_tokens'),
            'classes': ('collapse',)
        }),
        ('Usage Limits - Weekly', {
            'fields': ('weekly_max_messages', 'weekly_max_tokens'),
            'classes': ('collapse',)
        }),
        ('Usage Limits - Monthly', {
            'fields': ('monthly_max_messages', 'monthly_max_tokens', 'monthly_free_model_messages', 'monthly_free_model_tokens'),
            'classes': ('collapse',)
        }),
        ('Image Generation Limits', {
            'fields': ('daily_image_generation_limit', 'weekly_image_generation_limit', 'monthly_image_generation_limit'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'subscription_type', 'start_date')
    search_fields = ('user__name', 'user__phone_number')

@admin.register(UserUsage)
class UserUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'messages_count', 'tokens_count', 'created_at')
    list_filter = ('subscription_type', 'created_at')
    search_fields = ('user__name',)

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'uses_count', 'max_uses', 'expires_at')
    list_filter = ('discount_type', 'is_active', 'expires_at', 'created_at')
    search_fields = ('code',)
    filter_horizontal = ('subscription_types',)
    
    readonly_fields = ('uses_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Applicability', {
            'fields': ('subscription_types',)
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'max_uses_per_user')
        }),
        ('Validity', {
            'fields': ('expires_at', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('subscription_types')

@admin.register(DiscountUse)
class DiscountUseAdmin(admin.ModelAdmin):
    list_display = ('discount_code', 'user', 'subscription_type', 'original_price', 'discount_amount', 'final_price', 'used_at')
    list_filter = ('discount_code', 'subscription_type', 'used_at')
    search_fields = ('discount_code__code', 'user__name', 'user__phone_number')
    readonly_fields = ('used_at',)
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of discount uses


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'status', 'amount', 'authority', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__name', 'user__phone_number', 'authority', 'reference_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('user', 'subscription_type', 'transaction_type', 'status')
        }),
        ('Financial Details', {
            'fields': ('amount', 'original_amount', 'discount_amount', 'discount_code')
        }),
        ('Payment Gateway Details', {
            'fields': ('authority', 'reference_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DefaultSubscriptionSettings)
class DefaultSubscriptionSettingsAdmin(admin.ModelAdmin):
    list_display = ('setting_type_display', 'subscription_type', 'is_active_display', 'description_short', 'updated_at')
    list_filter = ('setting_type', 'is_active', 'created_at')
    search_fields = ('subscription_type__name', 'description')
    
    fieldsets = (
        ('تنظیمات اصلی', {
            'fields': ('setting_type', 'subscription_type', 'is_active')
        }),
        ('جزئیات', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def setting_type_display(self, obj):
        icons = {
            'new_user_default': '👤',
            'expired_fallback': '⏰'
        }
        icon = icons.get(obj.setting_type, '⚙️')
        return format_html(
            '<span style="font-size: 16px;">{} {}</span>',
            icon,
            obj.get_setting_type_display()
        )
    setting_type_display.short_description = 'نوع تنظیم'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ فعال</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ غیرفعال</span>'
            )
    is_active_display.short_description = 'وضعیت'
    
    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'توضیح'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscription_type')
    
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
            if change:
                messages.success(request, f'تنظیم "{obj.get_setting_type_display()}" با موفقیت به‌روزرسانی شد.')
            else:
                messages.success(request, f'تنظیم "{obj.get_setting_type_display()}" با موفقیت ایجاد شد.')
        except Exception as e:
            messages.error(request, f'خطا در ذخیره تنظیمات: {str(e)}')
    
    class Media:
        css = {
            'all': ('admin/css/default_subscription_settings.css',)
        }
    
    # افزودن اکشن برای فعال‌سازی سریع
    actions = ['activate_settings', 'deactivate_settings']
    
    def activate_settings(self, request, queryset):
        updated = queryset.update(is_active=True)
        messages.success(request, f'{updated} تنظیم فعال شد.')
    activate_settings.short_description = 'فعال‌سازی تنظیمات انتخابی'
    
    def deactivate_settings(self, request, queryset):
        updated = queryset.update(is_active=False)
        messages.warning(request, f'{updated} تنظیم غیرفعال شد.')
    deactivate_settings.short_description = 'غیرفعال‌سازی تنظیمات انتخابی'
