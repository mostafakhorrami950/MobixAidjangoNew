from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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
    
    def get_subscription_type(self, obj):
        try:
            return obj.subscription.subscription_type.name if obj.subscription.is_active else 'No Active Subscription'
        except:
            return 'No Subscription'
    get_subscription_type.short_description = 'Subscription Type'

admin.site.register(User, CustomUserAdmin)