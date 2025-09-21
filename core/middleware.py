"""
Middleware for optimizing subscription queries
"""
from django.utils.deprecation import MiddlewareMixin


class SubscriptionMiddleware(MiddlewareMixin):
    """
    Middleware to cache user subscription data to reduce database queries
    """
    
    def process_request(self, request):
        """
        Cache subscription data in request object if user is authenticated
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Cache subscription type to avoid repeated database queries
            try:
                subscription_type = request.user.get_subscription_type()
                request.cached_subscription_type = subscription_type
            except Exception:
                request.cached_subscription_type = None
            
            # Cache subscription info as well
            try:
                subscription_info = request.user.get_subscription_info()
                request.cached_subscription_info = subscription_info
            except Exception:
                request.cached_subscription_info = None
        
        return None