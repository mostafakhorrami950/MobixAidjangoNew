from django.contrib import admin
from .models import Chatbot, ChatSession, ChatMessage, GeneratedImage, UserUploadedImage, WebSearch, PDFDocument

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
    fields = ('name', 'description', 'chatbot_type', 'is_active', 'system_prompt', 'subscription_types')

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
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session__title', 'user__name')
    readonly_fields = ('id', 'created_at')

@admin.register(UserUploadedImage)
class UserUploadedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session__title', 'user__name')
    readonly_fields = ('id', 'created_at')

@admin.register(WebSearch)
class WebSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'query', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session__title', 'user__name', 'query')
    readonly_fields = ('id', 'created_at')

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'file_name', 'file_size', 'processing_engine', 'created_at', 'is_active')
    list_filter = ('is_active', 'processing_engine', 'created_at')
    search_fields = ('session__title', 'user__name', 'file_name')
    readonly_fields = ('id', 'created_at')
