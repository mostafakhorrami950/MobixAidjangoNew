from django.contrib import admin
from .models import AIModel, ModelSubscription, WebSearchSettings

class ModelSubscriptionInline(admin.TabularInline):
    model = ModelSubscription
    extra = 1

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'model_type', 'is_active', 'is_free', 'token_cost_multiplier', 'access_type', 'created_at')
    list_filter = ('model_type', 'is_active', 'is_free', 'created_at')
    search_fields = ('name', 'model_id')
    list_editable = ('is_active', 'is_free', 'token_cost_multiplier')
    inlines = [ModelSubscriptionInline]
    
    # Add image field to the admin form
    fields = ('name', 'model_id', 'description', 'model_type', 'is_active', 'is_free', 'token_cost_multiplier', 'image')
    
    @admin.display(description='Access Type')
    def access_type(self, obj):
        if obj.is_free:
            return "Free"
        elif obj.subscriptions.exists():
            subscription_types = obj.subscriptions.first().subscription_types.values_list('name', flat=True)
            return ", ".join(subscription_types) if subscription_types else "Premium Only"
        else:
            return "Not Available"

@admin.register(WebSearchSettings)
class WebSearchSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'web_search_model', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('enabled_subscription_types',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "web_search_model":
            kwargs["queryset"] = AIModel.objects.filter(model_type='text', is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)