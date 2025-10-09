from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.apps import apps
from .models import AIModel, ModelSubscription, WebSearchSettings, ModelArticle

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'model_type', 'is_active', 'is_free', 'token_cost_multiplier', 'created_at')
    list_filter = ('model_type', 'is_active', 'is_free', 'created_at')
    search_fields = ('name', 'model_id', 'description')
    list_editable = ('is_active', 'is_free', 'token_cost_multiplier')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'model_id', 'description', 'model_type')
        }),
        ('تنظیمات', {
            'fields': ('is_active', 'is_free', 'token_cost_multiplier', 'image')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article')
    
    def changelist_view(self, request, extra_context=None):
        # Add custom reports to the context
        extra_context = extra_context or {}
        
        # Get models using apps.get_model
        OpenRouterRequestCost = apps.get_model('chatbot', 'OpenRouterRequestCost')
        AIModel = apps.get_model('ai_models', 'AIModel')
        
        try:
            # Top AI models by usage count
            top_models = OpenRouterRequestCost.objects.values(
                'model_name'
            ).annotate(
                usage_count=Count('id'),
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('total_cost_usd')
            ).order_by('-usage_count')[:10]
            
            extra_context['top_models'] = list(top_models)
            
            # Top free AI models by usage
            top_free_models = OpenRouterRequestCost.objects.filter(
                model_name__in=AIModel.objects.filter(is_free=True).values_list('name', flat=True)
            ).values(
                'model_name'
            ).annotate(
                usage_count=Count('id'),
                total_tokens=Sum('total_tokens')
            ).order_by('-usage_count')[:10]
            
            extra_context['top_free_models'] = list(top_free_models)
        except Exception as e:
            # Handle timezone or other database errors gracefully
            extra_context['top_models'] = []
            extra_context['top_free_models'] = []
            extra_context['report_error'] = str(e)
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(ModelSubscription)
class ModelSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('ai_model', 'get_subscription_types')
    filter_horizontal = ('subscription_types',)
    
    @admin.display(description='انواع اشتراک')
    def get_subscription_types(self, obj):
        return ", ".join([str(st) for st in obj.subscription_types.all()])

@admin.register(WebSearchSettings)
class WebSearchSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'web_search_model', 'is_active')
    list_filter = ('is_active', 'created_at')
    filter_horizontal = ('enabled_subscription_types',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'web_search_model', 'is_active')
        }),
        ('دسترسی', {
            'fields': ('enabled_subscription_types',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ModelArticle)
class ModelArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'ai_model', 'is_published', 'show_login_register', 'created_at')
    list_filter = ('is_published', 'show_login_register', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    list_editable = ('is_published', 'show_login_register')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('ai_model', 'title', 'slug', 'excerpt', 'content')
        }),
        ('تصویر', {
            'fields': ('image',)
        }),
        ('انتشار', {
            'fields': ('is_published', 'show_login_register')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ai_model')