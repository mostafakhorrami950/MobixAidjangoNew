from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.apps import apps
from django.urls import reverse
from subscriptions.services import UsageService
from subscriptions.usage_stats import UserUsageStatsService
from .models import TermsAndConditions
from chatbot.models import SidebarMenuItem

def home(request):
    """
    Home page view - redirect authenticated users to chat
    """
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'home.html')

@login_required
def dashboard(request):
    """
    Dashboard page view with real-time user information
    """
    # Get models dynamically to avoid import issues
    UserSubscription = apps.get_model('subscriptions', 'UserSubscription')
    ChatSession = apps.get_model('chatbot', 'ChatSession')
    ChatMessage = apps.get_model('chatbot', 'ChatMessage')
    FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
    
    # Get user's subscription information
    try:
        user_subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).latest('end_date')
    except UserSubscription.DoesNotExist:
        user_subscription = None
    
    # Get user's chat sessions count
    session_count = ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).count()
    
    # Get user's message count
    message_count = ChatMessage.objects.filter(
        session__user=request.user
    ).count()
    
    # Get user's last activity (last message time)
    last_message = ChatMessage.objects.filter(
        session__user=request.user
    ).order_by('-created_at').first()
    
    last_activity = last_message.created_at if last_message else request.user.date_joined
    
    # Get user's recent sessions (last 5)
    recent_sessions = ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-updated_at')[:5]
    
    # Get user's recent financial transactions (last 5)
    recent_transactions = FinancialTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Get comprehensive usage statistics
    usage_stats = UserUsageStatsService.get_user_usage_statistics(request.user)
    usage_summary = UserUsageStatsService.get_usage_summary_for_dashboard(request.user)
    usage_cards = UserUsageStatsService.get_usage_cards_data(request.user)
    
    # Get user's token usage information (for backward compatibility)
    user_tokens_used = 0
    if user_subscription:
        # Calculate total tokens used using the new ChatSessionUsage method
        total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(
            request.user, user_subscription.subscription_type
        )
        user_tokens_used = total_tokens_used
    
    context = {
        'user_subscription': user_subscription,
        'session_count': session_count,
        'message_count': message_count,
        'last_activity': last_activity,
        'recent_sessions': recent_sessions,
        'recent_transactions': recent_transactions,
        'user_tokens_used': user_tokens_used,
        # Usage statistics
        'usage_stats': usage_stats,
        'usage_summary': usage_summary,
        'usage_cards': usage_cards,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def financial_transactions(request):
    """
    Display all financial transactions for the user with pagination
    """
    # Get model dynamically to avoid import issues
    FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
    
    # Get all financial transactions for the user, ordered by creation date
    transactions = FinancialTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Paginate the transactions (10 per page)
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
    }
    
    return render(request, 'financial_transactions.html', context)

def terms_and_conditions(request):
    """
    Display terms and conditions
    """
    terms = TermsAndConditions.get_active_terms()
    if not terms:
        # Create default terms if none exist
        terms = TermsAndConditions(
            title="شرایط و قوانین استفاده",
            content="""
            شرایط و قوانین استفاده از سرویس MobixAI:
            
            ۱. با استفاده از این سرویس، شما موافقت خود را با این شرایط اعلام می‌کنید.
            ۲. از سرویس در امور غیرقانونی استفاده نکنید.
            ۳. حریم خصوصی کاربران رعایت می‌شود.
            ۴. استفاده مناسب از منابع سرویس ضروری است.
            ۵. شرایط این قابل تغییر است.
            """.strip()
        )
        terms.save()
    
    context = {
        'terms': terms
    }
    return render(request, 'terms_and_conditions.html', context)

def get_random_advertising_banner(request):
    """
    Get a random active advertising banner
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        from .models import AdvertisingBanner
        from django.apps import apps
        from django.conf import settings
        
        # Check if user has premium subscription
        UserSubscription = apps.get_model('subscriptions', 'UserSubscription')
        has_premium = False
        if request.user.is_authenticated:
            try:
                user_subscription = UserSubscription.objects.filter(
                    user=request.user,
                    is_active=True
                ).latest('end_date')
                has_premium = user_subscription.subscription_type.name != 'Free'
            except UserSubscription.DoesNotExist:
                pass
        
        # Don't show banner to premium users
        if has_premium:
            return JsonResponse({
                'banner': None
            })
        
        # Get a random active banner
        banner = AdvertisingBanner.get_random_active_banner()
        
        if banner:
            banner_data = {
                'id': banner.id,
                'title': banner.title,
                'link': banner.link,
                'is_active': banner.is_active
            }
            
            # Add image URL if available
            if banner.image:
                # Use build_absolute_uri to create full URL
                banner_data['image_url'] = request.build_absolute_uri(banner.image.url)
            else:
                banner_data['image_url'] = None
            
            return JsonResponse({
                'banner': banner_data
            })
        else:
            return JsonResponse({
                'banner': None
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_sidebar_menu_items(request):
    """
    Get all active sidebar menu items that the user has permission to view
    This is a simplified version for non-chat pages
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        SidebarMenuItem = apps.get_model('chatbot', 'SidebarMenuItem')
        
        # Get all active menu items ordered by display order
        menu_items = SidebarMenuItem.objects.filter(is_active=True).order_by('order')
        
        # Filter items based on user permissions and authentication status
        user_menu_items = []
        for item in menu_items:
            # If item should only be shown to authenticated users and user is not authenticated, skip it
            if item.show_only_for_authenticated and not request.user.is_authenticated:
                continue
                
            # If item should only be shown to non-authenticated users and user is authenticated, skip it
            if item.show_only_for_non_authenticated and request.user.is_authenticated:
                continue
            
            # Resolve the URL
            try:
                # Handle namespaced URLs (e.g., 'chat:chat')
                if ':' in item.url_name:
                    url = reverse(item.url_name)
                else:
                    # Try to resolve as a chat app URL first, then fall back to global
                    try:
                        url = reverse(f'chat:{item.url_name}')
                    except:
                        url = reverse(item.url_name)
                user_menu_items.append({
                    'name': item.name,
                    'url': url,
                    'icon_class': item.icon_class,
                    'order': item.order,
                    'show_only_for_authenticated': item.show_only_for_authenticated,
                    'show_only_for_non_authenticated': item.show_only_for_non_authenticated
                })
            except:
                # Skip items with invalid URLs
                continue
        
        return JsonResponse({
            'menu_items': user_menu_items
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)