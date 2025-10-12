from django.contrib import admin
from .models import Chatbot, ChatSession, ChatMessage, UploadedFile, FileUploadSettings, VisionProcessingSettings, UploadedImage, FileUploadUsage, ImageGenerationUsage, DefaultChatSettings, SidebarMenuItem, LimitationMessage, OpenRouterRequestCost

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

from django.utils import timezone
import datetime

class OpenRouterRequestCostAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'total_tokens', 'formatted_created_at', 'formatted_updated_at')
    list_filter = ('model_name', 'request_type', 'subscription_type')
    search_fields = ('user__name', 'user__phone_number', 'model_name', 'model_id')
    readonly_fields = ('user', 'session', 'subscription_type', 'created_at', 'updated_at')
    date_hierarchy = None  # Disable date hierarchy to avoid timezone issues
    
    @admin.display(description='Created At')
    def formatted_created_at(self, obj):
        """
        Format created_at for display in admin, handling timezone issues
        """
        try:
            if obj.created_at:
                # If timezone-aware, convert to naive
                if timezone.is_aware(obj.created_at):
                    return timezone.localtime(obj.created_at).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
            return "-"
        except Exception:
            return "Invalid Date"
    
    @admin.display(description='Updated At')
    def formatted_updated_at(self, obj):
        """
        Format updated_at for display in admin, handling timezone issues
        """
        try:
            if obj.updated_at:
                # If timezone-aware, convert to naive
                if timezone.is_aware(obj.updated_at):
                    return timezone.localtime(obj.updated_at).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            return "-"
        except Exception:
            return "Invalid Date"

# Register the model with the custom admin class
admin.site.register(OpenRouterRequestCost, OpenRouterRequestCostAdmin)
