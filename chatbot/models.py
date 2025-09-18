from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User
from ai_models.models import AIModel
from subscriptions.models import SubscriptionType
import uuid

class Chatbot(models.Model):
    CHATBOT_TYPES = [
        ('text', 'Text Generator'),
        ('image_editing', 'Image Editing'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    subscription_types = models.ManyToManyField(SubscriptionType, blank=True, related_name='chatbots')
    is_active = models.BooleanField(default=True)
    system_prompt = models.TextField(blank=True, help_text="System prompt for the AI model")
    chatbot_type = models.CharField(max_length=20, choices=CHATBOT_TYPES, default='text', help_text="Type of chatbot (text generation)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        db_table = 'chatbots'

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, null=True, blank=True)
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, null=True, blank=True)  # Kept for backward compatibility
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def clean(self):
        # Ensure either chatbot or ai_model is set
        if not self.chatbot and not self.ai_model:
            raise ValidationError("Either chatbot or ai_model must be set.")
        # Allow both to be set for backward compatibility
        # Only enforce exclusive setting if both are explicitly set and not None
        if self.chatbot and self.ai_model:
            # This is allowed for backward compatibility
            pass
        
        # If chatbot is set, validate that it's active
        if self.chatbot and not self.chatbot.is_active:
            raise ValidationError("Selected chatbot is not active.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.chatbot:
            return f"{self.user.name} - {self.chatbot.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        elif self.ai_model:
            return f"{self.user.name} - {self.ai_model.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        else:
            return f"{self.user.name} - Unknown Model - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    tokens_count = models.IntegerField(default=0)
    image_url = models.TextField(blank=True)  # For image generation responses
    created_at = models.DateTimeField(default=timezone.now)
    
    # Add fields for message editing functionality
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    needs_regeneration = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    disabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

class ChatSessionUsage(models.Model):
    """
    Track token usage per chat session
    This model ensures that usage data is never deleted even if chat sessions are deleted
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='usage_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_session_usages')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    tokens_count = models.IntegerField(default=0, help_text="Total tokens used in this session")
    free_model_tokens_count = models.IntegerField(default=0, help_text="Tokens used with free models in this session")
    is_free_model = models.BooleanField(default=False, help_text="Whether this session used free models")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.session.title} - {self.tokens_count} tokens"
    
    class Meta:
        db_table = 'chat_session_usages'
        ordering = ['-created_at']


class UploadedFile(models.Model):
    """
    Model to track uploaded files with subscription-based restrictions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='uploaded_files')
    filename = models.CharField(max_length=255, help_text="Unique filename for storage")
    original_filename = models.CharField(max_length=255, help_text="Original filename from user")
    mimetype = models.CharField(max_length=100, help_text="MIME type of the file")
    size = models.PositiveIntegerField(help_text="File size in bytes")
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.name} - {self.original_filename}"
    
    class Meta:
        db_table = 'uploaded_files'
        ordering = ['-uploaded_at']


class FileUploadSettings(models.Model):
    """
    Model to manage file upload settings per subscription type
    """
    subscription_type = models.OneToOneField(SubscriptionType, on_delete=models.CASCADE, related_name='file_upload_settings')
    max_file_size = models.PositiveIntegerField(help_text="Maximum file size in bytes (0 for unlimited)")
    allowed_extensions = models.TextField(help_text="Comma-separated list of allowed file extensions")
    max_files_per_chat = models.PositiveIntegerField(help_text="Maximum files per chat session (0 for unlimited)")
    
    # Time-based limits for file uploads
    daily_file_limit = models.PositiveIntegerField(default=0, help_text="Maximum files per day (0 for unlimited)")
    weekly_file_limit = models.PositiveIntegerField(default=0, help_text="Maximum files per week (0 for unlimited)")
    monthly_file_limit = models.PositiveIntegerField(default=0, help_text="Maximum files per month (0 for unlimited)")
    
    is_active = models.BooleanField(default=True, help_text="Whether these settings are active")
    
    def __str__(self):
        return f"File settings for {self.subscription_type.name}"
    
    class Meta:
        db_table = 'file_upload_settings'
    
    def get_allowed_extensions_list(self):
        """Return allowed extensions as a list"""
        if self.allowed_extensions:
            return [ext.strip().lower() for ext in self.allowed_extensions.split(',')]
        return []


class VisionProcessingSettings(models.Model):
    """
    Model to configure which AI model should be used for vision/image processing
    """
    name = models.CharField(max_length=100, default="Vision Processing Settings")
    ai_model = models.ForeignKey(
        AIModel, 
        on_delete=models.CASCADE, 
        related_name='vision_processing_settings',
        help_text="AI model to use for vision/image processing and analysis"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Vision Processing Settings - {self.ai_model.name}"
    
    class Meta:
        db_table = 'vision_processing_settings'
        verbose_name = "Vision Processing Settings"
        verbose_name_plural = "Vision Processing Settings"


class UploadedImage(models.Model):
    """
    Model to store uploaded images for vision-capable AI models
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='uploaded_images')
    image_file = models.ImageField(upload_to='image_uploads/')
    analysis_result = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image uploaded by {self.user.username} for session {self.session.id}"
    
    class Meta:
        db_table = 'uploaded_images'
        ordering = ['-uploaded_at']


class FileUploadUsage(models.Model):
    """
    Model to track file upload usage per user and subscription type
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_upload_usage')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    
    # Usage counters for different time periods
    daily_files_count = models.PositiveIntegerField(default=0, help_text="Files uploaded today")
    weekly_files_count = models.PositiveIntegerField(default=0, help_text="Files uploaded this week")
    monthly_files_count = models.PositiveIntegerField(default=0, help_text="Files uploaded this month")
    session_files_count = models.PositiveIntegerField(default=0, help_text="Files uploaded in current session")
    
    # Timestamps for tracking periods
    daily_period_start = models.DateTimeField(help_text="Start of daily period")
    weekly_period_start = models.DateTimeField(help_text="Start of weekly period")
    monthly_period_start = models.DateTimeField(help_text="Start of monthly period")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.subscription_type.name} - File usage"
    
    class Meta:
        db_table = 'file_upload_usage'
        unique_together = ('user', 'subscription_type')


class DefaultChatSettings(models.Model):
    """
    مدل تنظیمات پیش‌فرض برای چت‌های جدید
    Default settings for new chat sessions when no specific session is selected
    """
    name = models.CharField(max_length=100, default="Default Chat Settings")
    default_chatbot = models.ForeignKey(
        Chatbot, 
        on_delete=models.CASCADE, 
        related_name='default_chat_settings',
        help_text="چت‌بات پیش‌فرض برای جلسات جدید"
    )
    default_ai_model = models.ForeignKey(
        AIModel, 
        on_delete=models.CASCADE, 
        related_name='default_chat_settings',
        help_text="مدل پیش‌فرض برای جلسات جدید"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.default_chatbot.name} - {self.default_ai_model.name}"
    
    class Meta:
        db_table = 'default_chat_settings'
        verbose_name = "Default Chat Settings"
        verbose_name_plural = "Default Chat Settings"


class ImageGenerationUsage(models.Model):
    """
    Model to track image generation usage per user and subscription type
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_generation_usage')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    
    # Usage counters for different time periods
    daily_images_count = models.PositiveIntegerField(default=0, help_text="Images generated today")
    weekly_images_count = models.PositiveIntegerField(default=0, help_text="Images generated this week")
    monthly_images_count = models.PositiveIntegerField(default=0, help_text="Images generated this month")
    
    # Timestamps for tracking periods
    daily_period_start = models.DateTimeField(help_text="Start of daily period")
    weekly_period_start = models.DateTimeField(help_text="Start of weekly period")
    monthly_period_start = models.DateTimeField(help_text="Start of monthly period")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.subscription_type.name} - Image generation usage"
    
    class Meta:
        db_table = 'image_generation_usage'
        unique_together = ('user', 'subscription_type')


class MessageFile(models.Model):
    """
    Model to store multiple files for a single message
    رابطه چند-به-چند بین پیام‌ها و فایل‌ها
    """
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='uploaded_files')
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='message_files')
    file_order = models.PositiveIntegerField(default=0, help_text="Order of file in the message")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"File {self.uploaded_file.original_filename} for message {self.message.message_id}"
    
    class Meta:
        db_table = 'message_files'
        ordering = ['file_order', 'created_at']
        unique_together = ('message', 'uploaded_file')


class SidebarMenuItem(models.Model):
    """
    Model for configurable sidebar menu items
    """
    name = models.CharField(max_length=100, help_text="Display name of the menu item")
    url_name = models.CharField(max_length=100, help_text="Django URL name")
    icon_class = models.CharField(max_length=50, default='fas fa-link', help_text="Font Awesome icon class")
    order = models.PositiveIntegerField(default=0, help_text="Order of display (lower numbers first)")
    is_active = models.BooleanField(default=True)
    required_permission = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Required permission to view this item (optional)"
    )
    show_only_for_authenticated = models.BooleanField(
        default=False,
        help_text="If True, this menu item will only be shown to authenticated users"
    )
    show_only_for_non_authenticated = models.BooleanField(
        default=False,
        help_text="If True, this menu item will only be shown to non-authenticated users"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'sidebar_menu_items'
        ordering = ['order', 'name']
