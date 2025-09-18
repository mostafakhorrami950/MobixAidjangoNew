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
        ('image', 'Image Generator'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    subscription_types = models.ManyToManyField(SubscriptionType, blank=True, related_name='chatbots')
    is_active = models.BooleanField(default=True)
    system_prompt = models.TextField(blank=True, help_text="System prompt for the AI model")
    chatbot_type = models.CharField(max_length=10, choices=CHATBOT_TYPES, default='text', help_text="Type of chatbot (text or image generation)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
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


class GeneratedImage(models.Model):
    """
    Model to store generated images
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='generated_images')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_images')
    image = models.ImageField(upload_to='generated_images/')
    original_prompt = models.TextField(blank=True, help_text="The original prompt used to generate this image")
    modification_prompt = models.TextField(blank=True, help_text="The prompt used to modify this image")
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Image {self.id} - {self.session.title}"
    
    class Meta:
        db_table = 'generated_images'
        ordering = ['-created_at']


class UserUploadedImage(models.Model):
    """
    Model to store user uploaded images
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='uploaded_images')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images')
    image = models.ImageField(upload_to='user_uploaded_images/')
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"User Image {self.id} - {self.session.title}"
    
    class Meta:
        db_table = 'user_uploaded_images'
        ordering = ['-created_at']


class WebSearch(models.Model):
    """
    Model to store web search information
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='web_searches')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='web_searches')
    query = models.TextField(help_text="The search query used")
    search_results = models.TextField(blank=True, help_text="The search results returned")
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Web Search {self.id} - {self.session.title}"
    
    class Meta:
        db_table = 'web_searches'
        ordering = ['-created_at']


class PDFDocument(models.Model):
    """
    Model to store PDF document information
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='pdf_documents')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_documents')
    pdf_file = models.FileField(upload_to='pdf_documents/')
    file_name = models.CharField(max_length=255, help_text="Original file name")
    file_size = models.IntegerField(help_text="File size in bytes")
    processing_engine = models.CharField(max_length=50, help_text="The engine used to process the PDF (pdf-text, mistral-ocr, native)")
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"PDF Document {self.id} - {self.file_name}"
    
    class Meta:
        db_table = 'pdf_documents'
        ordering = ['-created_at']

