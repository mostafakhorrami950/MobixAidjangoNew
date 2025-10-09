from django.contrib import admin
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from django.apps import apps
from django.db.models.functions import TruncDate
from .models import Chatbot, ChatSession, ChatMessage, UploadedFile, FileUploadSettings, VisionProcessingSettings, UploadedImage, FileUploadUsage, ImageGenerationUsage, DefaultChatSettings, SidebarMenuItem, LimitationMessage, OpenRouterRequestCost
from accounts.models import User
from ai_models.models import AIModel
from subscriptions.models import SubscriptionType, UserSubscription

class ChatSessionInline(admin.TabularInline):
    model = ChatSession
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Chatbot)
class ChatbotAdmin(admin.ModelAdmin):
    list_display = ('name', 'chatbot_type', 'is_active', 'created_at')
    list_filter = ('chatbot_type', 'is_active', 'subscription_types', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    filter_horizontal = ('subscription_types',)
    inlines = [ChatSessionInline]
    fields = ('name', 'description', 'image', 'chatbot_type', 'is_active', 'system_prompt', 'subscription_types')

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'chatbot', 'title', 'created_at', 'updated_at', 'is_active')
    list_filter = ('chatbot', 'is_active', 'created_at', 'updated_at')
    search_fields = ('user__name', 'user__phone_number', 'title')
    inlines = [ChatMessageInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'message_type', 'content_preview', 'tokens_count', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('content', 'session__user__name')
    readonly_fields = ('created_at',)
    
    @admin.display(description='Content Preview')
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'original_filename', 'size', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('original_filename', 'user__name', 'user__phone_number')
    readonly_fields = ('filename', 'original_filename', 'mimetype', 'size', 'uploaded_at')

@admin.register(FileUploadSettings)
class FileUploadSettingsAdmin(admin.ModelAdmin):
    list_display = ('subscription_type', 'max_file_size', 'max_files_per_chat', 
                   'daily_file_limit', 'weekly_file_limit', 'monthly_file_limit', 'is_active')
    list_filter = ('subscription_type', 'is_active')
    search_fields = ('subscription_type__name',)
    fields = ('subscription_type', 'max_file_size', 'allowed_extensions', 
              'max_files_per_chat', 'daily_file_limit', 'weekly_file_limit', 
              'monthly_file_limit', 'is_active')

@admin.register(FileUploadUsage)
class FileUploadUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'daily_files_count', 
                   'weekly_files_count', 'monthly_files_count', 'session_files_count')
    list_filter = ('subscription_type', 'user')
    search_fields = ('user__name', 'user__phone_number')
    readonly_fields = ('daily_period_start', 'weekly_period_start', 'monthly_period_start', 
                      'created_at', 'updated_at')

@admin.register(ImageGenerationUsage)
class ImageGenerationUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'daily_images_count', 
                   'weekly_images_count', 'monthly_images_count')
    list_filter = ('subscription_type', 'user')
    search_fields = ('user__name', 'user__phone_number')
    readonly_fields = ('daily_period_start', 'weekly_period_start', 'monthly_period_start', 
                      'created_at', 'updated_at')

@admin.register(DefaultChatSettings)
class DefaultChatSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_chatbot', 'default_ai_model', 'is_active', 'created_at')
    list_filter = ('is_active', 'default_chatbot', 'created_at')
    search_fields = ('name', 'default_chatbot__name', 'default_ai_model__name')
    fields = ('name', 'default_chatbot', 'default_ai_model', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(VisionProcessingSettings)
class VisionProcessingSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'ai_model', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'ai_model__name')
    fields = ('name', 'ai_model', 'is_active')

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__name', 'session__title')
    readonly_fields = ('uploaded_at',)

@admin.register(SidebarMenuItem)
class SidebarMenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_name', 'icon_class', 'order', 'is_active', 'show_only_for_authenticated', 'show_only_for_non_authenticated', 'required_permission')
    list_filter = ('is_active', 'show_only_for_authenticated', 'show_only_for_non_authenticated', 'created_at', 'updated_at')
    search_fields = ('name', 'url_name', 'required_permission')
    list_editable = ('order', 'is_active', 'show_only_for_authenticated', 'show_only_for_non_authenticated')
    fields = ('name', 'url_name', 'icon_class', 'order', 'is_active', 'show_only_for_authenticated', 'show_only_for_non_authenticated', 'required_permission')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LimitationMessage)
class LimitationMessageAdmin(admin.ModelAdmin):
    list_display = ('limitation_type', 'title', 'is_active', 'updated_at')
    list_filter = ('limitation_type', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'message', 'limitation_type')
    list_editable = ('is_active',)
    fields = ('limitation_type', 'title', 'message', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    
    # Removed custom form handling due to linter issues

@admin.register(OpenRouterRequestCost)
class OpenRouterRequestCostAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'total_tokens', 'total_cost_usd', 'request_type', 'created_at')
    list_filter = ('request_type', 'model_name', 'subscription_type', 'created_at')
    search_fields = ('user__name', 'user__phone_number', 'model_name', 'model_id')
    readonly_fields = ('created_at', 'updated_at')
    
    # Add date hierarchy for easier navigation
    date_hierarchy = 'created_at'
    
    # Add fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'session', 'subscription_type', 'request_type')
        }),
        ('Model Information', {
            'fields': ('model_id', 'model_name')
        }),
        ('Token Usage', {
            'fields': ('prompt_tokens', 'completion_tokens', 'total_tokens')
        }),
        ('Cost Information', {
            'fields': ('token_cost_multiplier', 'effective_cost_tokens', 'cost_per_million_tokens', 'total_cost_usd')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def changelist_view(self, request, extra_context=None):
        # Add custom reports to the context
        extra_context = extra_context or {}
        
        # Get models using apps.get_model
        OpenRouterRequestCost = apps.get_model('chatbot', 'OpenRouterRequestCost')
        AIModel = apps.get_model('ai_models', 'AIModel')
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        
        try:
            # Get data for reports
            
            # 1. Top users by cost
            top_users_cost = OpenRouterRequestCost.objects.values(
                'user__name',
                'user__phone_number'
            ).annotate(
                total_cost=Sum('total_cost_usd'),
                total_tokens=Sum('total_tokens'),
                request_count=Count('id')
            ).order_by('-total_cost')[:10]
            
            # 2. Top models by usage
            top_models_usage = OpenRouterRequestCost.objects.values(
                'model_name'
            ).annotate(
                usage_count=Count('id'),
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('total_cost_usd')
            ).order_by('-usage_count')[:10]
            
            # 3. Top free models usage
            free_models = AIModel.objects.filter(is_free=True).values_list('model_id', flat=True)
            top_free_models_usage = OpenRouterRequestCost.objects.filter(
                model_id__in=free_models
            ).values(
                'model_name'
            ).annotate(
                usage_count=Count('id'),
                total_tokens=Sum('total_tokens')
            ).order_by('-usage_count')[:10]
            
            # 4. Average token usage
            avg_tokens = OpenRouterRequestCost.objects.aggregate(
                avg_tokens=Avg('total_tokens')
            )
            
            # 5. Top chatbots by session count
            top_chatbots = ChatSession.objects.values(
                'chatbot__name'
            ).annotate(
                session_count=Count('id'),
                total_messages=Count('messages')
            ).order_by('-session_count')[:10]
            
            # Add to context
            extra_context.update({
                'top_users_cost': list(top_users_cost),
                'top_models_usage': list(top_models_usage),
                'top_free_models_usage': list(top_free_models_usage),
                'avg_tokens_per_request': avg_tokens['avg_tokens'] or 0,
                'top_chatbots': list(top_chatbots),
            })
        except Exception as e:
            # Handle timezone or other database errors gracefully
            extra_context.update({
                'top_users_cost': [],
                'top_models_usage': [],
                'top_free_models_usage': [],
                'avg_tokens_per_request': 0,
                'top_chatbots': [],
                'report_error': str(e)
            })
        
        return super().changelist_view(request, extra_context=extra_context)

# Enhanced Chatbot admin with reporting capabilities
class ChatbotAdminWithReports(ChatbotAdmin):
    """Enhanced Chatbot admin with reporting capabilities"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        # Add custom reports to the context
        extra_context = extra_context or {}
        
        # Get models using apps.get_model
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        
        try:
            # Get top chatbots by usage
            top_chatbots = ChatSession.objects.values(
                'chatbot__name'
            ).annotate(
                session_count=Count('id'),
                total_messages=Count('messages')
            ).order_by('-session_count')[:10]
            
            extra_context['top_chatbots'] = list(top_chatbots)
        except Exception as e:
            # Handle timezone or other database errors gracefully
            extra_context['top_chatbots'] = []
            extra_context['report_error'] = str(e)
        
        return super().changelist_view(request, extra_context=extra_context)