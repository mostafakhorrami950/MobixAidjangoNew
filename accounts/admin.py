from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum, Count, Avg
from django.apps import apps
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('phone_number', 'name', 'is_verified', 'is_staff', 'created_at', 'get_subscription_type')
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'created_at', 'subscription__subscription_type')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'password1', 'password2', 'is_verified', 'is_staff')}
        ),
    )
    search_fields = ('phone_number', 'name')
    ordering = ('phone_number',)
    readonly_fields = ('created_at',)
    
    @admin.display(description='Subscription Type')
    def get_subscription_type(self, obj):
        try:
            return obj.subscription.subscription_type.name if obj.subscription.is_active else 'No Active Subscription'
        except:
            return 'No Subscription'
    
    def changelist_view(self, request, extra_context=None):
        # Add custom reports to the context
        extra_context = extra_context or {}
        
        # Get models using apps.get_model
        OpenRouterRequestCost = apps.get_model('chatbot', 'OpenRouterRequestCost')
        AIModel = apps.get_model('ai_models', 'AIModel')
        
        try:
            # Top users by OpenRouter cost
            top_cost_users = OpenRouterRequestCost.objects.values(
                'user__name',
                'user__phone_number'
            ).annotate(
                total_cost=Sum('total_cost_usd'),
                total_tokens=Sum('total_tokens'),
                request_count=Count('id')
            ).order_by('-total_cost')[:10]
            
            extra_context['top_cost_users'] = list(top_cost_users)
            
            # Top users by free model usage
            free_models = AIModel.objects.filter(is_free=True).values_list('model_id', flat=True)
            top_free_users = OpenRouterRequestCost.objects.filter(
                model_id__in=free_models
            ).values(
                'user__name',
                'user__phone_number'
            ).annotate(
                total_tokens=Sum('total_tokens'),
                request_count=Count('id')
            ).order_by('-total_tokens')[:10]
            
            extra_context['top_free_users'] = list(top_free_users)
            
            # Average token usage per user
            avg_tokens = OpenRouterRequestCost.objects.aggregate(
                avg_tokens=Avg('total_tokens')
            )
            
            extra_context['avg_tokens_per_user'] = avg_tokens['avg_tokens'] or 0
        except Exception as e:
            # Handle timezone or other database errors gracefully
            extra_context['top_cost_users'] = []
            extra_context['top_free_users'] = []
            extra_context['avg_tokens_per_user'] = 0
            extra_context['report_error'] = str(e)
        
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(User, CustomUserAdmin)