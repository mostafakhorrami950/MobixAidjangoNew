from django.contrib import admin
from .models import GlobalSettings


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
