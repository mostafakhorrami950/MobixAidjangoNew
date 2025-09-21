#!/usr/bin/env python
"""
Test script to verify the cost multiplier functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from ai_models.models import AIModel
from subscriptions.services import UsageService
from subscriptions.models import SubscriptionType, UserUsage
from accounts.models import User
from django.utils import timezone

def test_cost_multiplier():
    print("Testing cost multiplier functionality...")
    
    # Get the existing AI model
    ai_model = AIModel.objects.first()
    print(f"Using AI Model: {ai_model.name}")
    print(f"Original cost multiplier: {ai_model.token_cost_multiplier}")
    
    # Create a test user if one doesn't exist
    user, created = User.objects.get_or_create(
        phone_number='09123456789',
        defaults={'name': 'Test User', 'username': '09123456789'}
    )
    print(f"User: {user.name}")
    
    # Create a basic subscription type if one doesn't exist
    subscription_type, created = SubscriptionType.objects.get_or_create(
        name='Test',
        defaults={
            'price': 0,
            'duration_days': 30,
            'sku': 'TEST001',
            'max_tokens': 1000,
            'max_tokens_free': 500
        }
    )
    print(f"Subscription Type: {subscription_type.name}")
    
    # Test 1: Normal usage without cost multiplier (should be 100 tokens)
    print("\n--- Test 1: Normal usage (multiplier = 1.0) ---")
    ai_model.token_cost_multiplier = 1.0
    ai_model.save()
    
    # Clear any existing usage records
    UserUsage.objects.filter(user=user, subscription_type=subscription_type).delete()
    
    UsageService.increment_usage(
        user=user,
        subscription_type=subscription_type,
        messages_count=1,
        tokens_count=100,
        is_free_model=False,
        ai_model=ai_model
    )
    
    # Check the usage record
    usage = UserUsage.objects.filter(user=user, subscription_type=subscription_type).first()
    print(f"Tokens recorded: {usage.tokens_count}")
    print(f"Expected: 100, Actual: {usage.tokens_count}, Test 1: {'PASS' if usage.tokens_count == 100 else 'FAIL'}")
    
    # Test 2: Usage with cost multiplier of 2.0 (should be 200 tokens)
    print("\n--- Test 2: Usage with multiplier = 2.0 ---")
    ai_model.token_cost_multiplier = 2.0
    ai_model.save()
    
    UsageService.increment_usage(
        user=user,
        subscription_type=subscription_type,
        messages_count=1,
        tokens_count=100,
        is_free_model=False,
        ai_model=ai_model
    )
    
    # Check the latest usage record
    usage = UserUsage.objects.filter(user=user, subscription_type=subscription_type).order_by('-created_at').first()
    print(f"Tokens recorded: {usage.tokens_count}")
    print(f"Expected: 200, Actual: {usage.tokens_count}, Test 2: {'PASS' if usage.tokens_count == 200 else 'FAIL'}")
    
    # Test 3: Usage with cost multiplier of 1.5 (should be 150 tokens)
    print("\n--- Test 3: Usage with multiplier = 1.5 ---")
    ai_model.token_cost_multiplier = 1.5
    ai_model.save()
    
    UsageService.increment_usage(
        user=user,
        subscription_type=subscription_type,
        messages_count=1,
        tokens_count=100,
        is_free_model=False,
        ai_model=ai_model
    )
    
    # Check the latest usage record
    usage = UserUsage.objects.filter(user=user, subscription_type=subscription_type).order_by('-created_at').first()
    print(f"Tokens recorded: {usage.tokens_count}")
    print(f"Expected: 150, Actual: {usage.tokens_count}, Test 3: {'PASS' if usage.tokens_count == 150 else 'FAIL'}")
    
    # Test 4: Free model (should ignore multiplier and record original tokens)
    print("\n--- Test 4: Free model (should ignore multiplier) ---")
    ai_model.token_cost_multiplier = 3.0  # Set high multiplier
    ai_model.save()
    
    UsageService.increment_usage(
        user=user,
        subscription_type=subscription_type,
        messages_count=1,
        tokens_count=100,
        is_free_model=True,  # This is a free model
        ai_model=ai_model
    )
    
    # Check the latest usage record (should be in free_model_tokens_count)
    usage = UserUsage.objects.filter(user=user, subscription_type=subscription_type).order_by('-created_at').first()
    print(f"Free model tokens recorded: {usage.free_model_tokens_count}")
    print(f"Expected: 100, Actual: {usage.free_model_tokens_count}, Test 4: {'PASS' if usage.free_model_tokens_count == 100 else 'FAIL'}")
    
    print("\n--- Test Summary ---")
    print("All tests completed. Check results above.")

if __name__ == '__main__':
    test_cost_multiplier()