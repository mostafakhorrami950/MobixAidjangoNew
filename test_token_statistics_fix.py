#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.apps import apps
from subscriptions.services import UsageService
from subscriptions.usage_stats import UserUsageStatsService

def test_token_statistics():
    """Test the token statistics calculation fix"""
    try:
        # Get the first user
        User = get_user_model()
        user = User.objects.first()
        
        if not user:
            print("❌ No user found in database")
            return
            
        print(f"✅ Testing token statistics for user: {user.name}")
        
        # Get user's subscription
        subscription_type = user.get_subscription_type()
        if not subscription_type:
            print("❌ No active subscription found for user")
            return
            
        print(f"✅ User subscription: {subscription_type.name}")
        
        # Test the get_user_total_tokens_from_chat_sessions method
        print("\n--- Testing get_user_total_tokens_from_chat_sessions ---")
        total_paid_tokens, total_free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(
            user, subscription_type
        )
        total_tokens = total_paid_tokens + total_free_tokens
        
        print(f"💰 Paid tokens used: {total_paid_tokens}")
        print(f"🆓 Free tokens used: {total_free_tokens}")
        print(f"📊 Total tokens used: {total_tokens}")
        
        # Test the UserUsageStatsService
        print("\n--- Testing UserUsageStatsService ---")
        stats = UserUsageStatsService.get_user_usage_statistics(user)
        
        if 'tokens' in stats:
            tokens_stats = stats['tokens']
            print(f"💰 Paid tokens - Used: {tokens_stats['paid']['used']}, Limit: {tokens_stats['paid']['limit']}")
            print(f"🆓 Free tokens - Used: {tokens_stats['free']['used']}, Limit: {tokens_stats['free']['limit']}")
            
            # Verify the values match
            if tokens_stats['paid']['used'] == total_paid_tokens and tokens_stats['free']['used'] == total_free_tokens:
                print("✅ Token statistics calculation is correct!")
            else:
                print("❌ Token statistics calculation mismatch!")
                print(f"   Expected paid: {total_paid_tokens}, got: {tokens_stats['paid']['used']}")
                print(f"   Expected free: {total_free_tokens}, got: {tokens_stats['free']['used']}")
        else:
            print("❌ No token statistics found")
            
        # Test the dashboard summary
        print("\n--- Testing dashboard summary ---")
        dashboard_summary = UserUsageStatsService.get_usage_summary_for_dashboard(user)
        
        if 'tokens_summary' in dashboard_summary:
            tokens_summary = dashboard_summary['tokens_summary']
            print(f"💰 Dashboard paid tokens: {tokens_summary['paid_used']}")
            print(f"🆓 Dashboard free tokens: {tokens_summary['free_used']}")
            
            # Verify the values match
            if tokens_summary['paid_used'] == total_paid_tokens and tokens_summary['free_used'] == total_free_tokens:
                print("✅ Dashboard token summary is correct!")
            else:
                print("❌ Dashboard token summary mismatch!")
        else:
            print("❌ No token summary found in dashboard")
            
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_token_statistics()