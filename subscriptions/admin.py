from django.contrib import admin
from .models import SubscriptionType, UserSubscription, UserUsage, DiscountCode, DiscountUse, FinancialTransaction

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