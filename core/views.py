from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.apps import apps
from subscriptions.services import UsageService

def home(request):
    """
    Home page view
    """
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
    
    # Get user's token usage information
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