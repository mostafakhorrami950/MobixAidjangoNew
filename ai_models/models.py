from django.db import models
from django.utils import timezone

class AIModel(models.Model):
    MODEL_TYPES = [
        ('text', 'Text Generation'),
        ('image', 'Image Generation'),
    ]
    
    name = models.CharField(max_length=100)
    model_id = models.CharField(max_length=100, unique=True)  # OpenRouter model ID
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=10, choices=MODEL_TYPES, default='text')
    is_active = models.BooleanField(default=True)
    is_free = models.BooleanField(default=False)  # Available for all registered users
    
    # Add the token cost multiplier field
    token_cost_multiplier = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.00, 
        help_text="Cost multiplier for this model. Example: 2.0 means double the cost."
    )
    
    # Add image field for model
    image = models.ImageField(
        upload_to='model_images/', 
        blank=True, 
        null=True,
        help_text="Image for this AI model"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.model_id})"
    
    class Meta:
        db_table = 'ai_models'

class ModelSubscription(models.Model):
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='subscriptions')
    subscription_types = models.ManyToManyField('subscriptions.SubscriptionType', related_name='ai_models')
    
    def __str__(self):
        return f"{self.ai_model.name} - Subscriptions"
    
    class Meta:
        db_table = 'model_subscriptions'

class WebSearchSettings(models.Model):
    """Settings for web search functionality"""
    name = models.CharField(max_length=100, default="Web Search Settings")
    web_search_model = models.ForeignKey(
        AIModel, 
        on_delete=models.CASCADE, 
        related_name='web_search_settings',
        help_text="AI model to use for web search functionality"
    )
    enabled_subscription_types = models.ManyToManyField(
        'subscriptions.SubscriptionType',
        blank=True,
        help_text="Subscription types that can use web search functionality"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'web_search_settings'
        verbose_name = "Web Search Settings"
        verbose_name_plural = "Web Search Settings"