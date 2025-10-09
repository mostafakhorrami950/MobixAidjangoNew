from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.apps import apps
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User as DjangoUser
from accounts.models import User
from django.contrib.auth.admin import UserAdmin


class ReportsAdminSite(AdminSite):
    site_header = "MobixAI Reports Administration"
    site_title = "MobixAI Reports Admin"
    index_title = "Reports Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.reports_dashboard), name='reports_dashboard'),
        ]
        return custom_urls + urls

    def reports_dashboard(self, request):
        # Check if user is superuser
        if not request.user.is_superuser:
            # Redirect or show error if not superuser
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access denied. Superuser access required.")
        
        # Get models using apps.get_model
        OpenRouterRequestCost = apps.get_model('chatbot', 'OpenRouterRequestCost')
        AIModel = apps.get_model('ai_models', 'AIModel')
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        
        context = dict(
            self.each_context(request),
        )
        
        try:
            # 1. Top users by OpenRouter cost
            top_users_cost = OpenRouterRequestCost.objects.values(
                'user__name',
                'user__phone_number'
            ).annotate(
                total_cost=Sum('total_cost_usd'),
                total_tokens=Sum('total_tokens'),
                request_count=Count('id')
            ).order_by('-total_cost')[:10]
            
            context['top_users_cost'] = list(top_users_cost)
            
            # 2. Top users by free model usage
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
            
            context['top_free_users'] = list(top_free_users)
            
            # 3. Average token usage
            avg_tokens = OpenRouterRequestCost.objects.aggregate(
                avg_tokens=Avg('total_tokens')
            )
            
            context['avg_tokens_per_request'] = avg_tokens['avg_tokens'] or 0
            
            # 4. Top chatbots by usage
            top_chatbots = ChatSession.objects.values(
                'chatbot__name'
            ).annotate(
                session_count=Count('id'),
                total_messages=Count('messages')
            ).order_by('-session_count')[:10]
            
            context['top_chatbots'] = list(top_chatbots)
            
            # 5. Top AI models by usage
            top_models = OpenRouterRequestCost.objects.values(
                'model_name'
            ).annotate(
                usage_count=Count('id'),
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('total_cost_usd')
            ).order_by('-usage_count')[:10]
            
            context['top_models'] = list(top_models)
            
            # 6. Top free AI models usage
            top_free_models = OpenRouterRequestCost.objects.filter(
                model_name__in=AIModel.objects.filter(is_free=True).values_list('name', flat=True)
            ).values(
                'model_name'
            ).annotate(
                usage_count=Count('id'),
                total_tokens=Sum('total_tokens')
            ).order_by('-usage_count')[:10]
            
            context['top_free_models'] = list(top_free_models)
            
        except Exception as e:
            # Handle timezone or other database errors gracefully
            context['top_users_cost'] = []
            context['top_free_users'] = []
            context['avg_tokens_per_request'] = 0
            context['top_chatbots'] = []
            context['top_models'] = []
            context['top_free_models'] = []
            context['report_error'] = str(e)
        
        return render(request, 'reports/dashboard.html', context)


# Create an instance of our custom admin site
reports_admin_site = ReportsAdminSite(name='reports_admin')


# Register the built-in User model with our custom admin site for superuser management
class SuperUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

reports_admin_site.register(DjangoUser, SuperUserAdmin)