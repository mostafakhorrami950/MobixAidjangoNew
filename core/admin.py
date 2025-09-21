from django.contrib import admin
from .models import GlobalSettings, TermsAndConditions


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'max_file_size_mb', 'max_files_per_message', 
        'session_timeout_hours', 'messages_per_page', 
        'api_requests_per_minute', 'is_active', 'updated_at'
    )
    
    fieldsets = (
        ('File Upload Settings', {
            'fields': ('max_file_size_mb', 'max_files_per_message', 'allowed_file_extensions')
        }),
        ('Security Settings', {
            'fields': ('session_timeout_hours',)
        }),
        ('Performance Settings', {
            'fields': ('messages_per_page', 'api_requests_per_minute')
        }),
        ('System', {
            'fields': ('is_active',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Allow adding only if no GlobalSettings exists
        return not GlobalSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of GlobalSettings
        return False


@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'updated_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'is_active')
        }),
        ('تاریخ ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion if this is the only active terms
        if obj and obj.is_active:
            active_terms_count = TermsAndConditions.objects.filter(is_active=True).count()
            if active_terms_count <= 1:
                return False
        return True
