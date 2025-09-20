from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionType

class Command(BaseCommand):
    help = 'Populate initial subscription types and usage limits'

    def handle(self, *args, **options):
        # Create subscription types
        free_subscription, created = SubscriptionType.objects.get_or_create(
            name='Free',
            defaults={
                'description': 'Free subscription with limited access',
                'price': 0,
                'duration_days': 30,
                'sku': 'FREE_SUB_30D',
                'max_tokens': 10000,
                'hourly_max_messages': 5,
                'hourly_max_tokens': 5000,
                'three_hours_max_messages': 10,
                'three_hours_max_tokens': 10000,
                'twelve_hours_max_messages': 20,
                'twelve_hours_max_tokens': 20000,
                'daily_max_messages': 20,
                'daily_max_tokens': 20000,
                'weekly_max_messages': 100,
                'weekly_max_tokens': 100000,
                'monthly_max_messages': 300,
                'monthly_max_tokens': 500000,
                'monthly_free_model_messages': 500,
                'monthly_free_model_tokens': 500000,
                'daily_image_generation_limit': 10,
                'weekly_image_generation_limit': 50,
                'monthly_image_generation_limit': 200,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {free_subscription.name} subscription')
            )
        else:
            # Update existing Free subscription with correct values
            free_subscription.description = 'Free subscription with limited access'
            free_subscription.price = 0
            free_subscription.duration_days = 30
            free_subscription.sku = 'FREE_SUB_30D'
            free_subscription.max_tokens = 10000
            free_subscription.hourly_max_messages = 5
            free_subscription.hourly_max_tokens = 5000
            free_subscription.three_hours_max_messages = 10
            free_subscription.three_hours_max_tokens = 10000
            free_subscription.twelve_hours_max_messages = 20
            free_subscription.twelve_hours_max_tokens = 20000
            free_subscription.daily_max_messages = 20
            free_subscription.daily_max_tokens = 20000
            free_subscription.weekly_max_messages = 100
            free_subscription.weekly_max_tokens = 100000
            free_subscription.monthly_max_messages = 300
            free_subscription.monthly_max_tokens = 500000
            free_subscription.monthly_free_model_messages = 500
            free_subscription.monthly_free_model_tokens = 500000
            free_subscription.daily_image_generation_limit = 10
            free_subscription.weekly_image_generation_limit = 50
            free_subscription.monthly_image_generation_limit = 200
            free_subscription.is_active = True
            free_subscription.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated {free_subscription.name} subscription')
            )
        
        premium_subscription, created = SubscriptionType.objects.get_or_create(
            name='Premium',
            defaults={
                'description': 'Premium subscription with full access',
                'price': 29.99,
                'duration_days': 30,
                'sku': 'PREMIUM_SUB_30D',
                'max_tokens': 0,  # Unlimited
                'hourly_max_messages': 20,
                'hourly_max_tokens': 20000,
                'three_hours_max_messages': 50,
                'three_hours_max_tokens': 100000,
                'twelve_hours_max_messages': 200,
                'twelve_hours_max_tokens': 500000,
                'daily_max_messages': 500,
                'daily_max_tokens': 1000000,
                'weekly_max_messages': 2000,
                'weekly_max_tokens': 5000000,
                'monthly_max_messages': 5000,
                'monthly_max_tokens': 20000000,
                'monthly_free_model_messages': 10000,
                'monthly_free_model_tokens': 10000000,
                'daily_image_generation_limit': 100,
                'weekly_image_generation_limit': 500,
                'monthly_image_generation_limit': 2000,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {premium_subscription.name} subscription')
            )
        else:
            # Update existing Premium subscription with correct values
            premium_subscription.description = 'Premium subscription with full access'
            premium_subscription.price = 29.99
            premium_subscription.duration_days = 30
            premium_subscription.sku = 'PREMIUM_SUB_30D'
            premium_subscription.max_tokens = 0  # Unlimited
            premium_subscription.hourly_max_messages = 20
            premium_subscription.hourly_max_tokens = 20000
            premium_subscription.three_hours_max_messages = 50
            premium_subscription.three_hours_max_tokens = 100000
            premium_subscription.twelve_hours_max_messages = 200
            premium_subscription.twelve_hours_max_tokens = 500000
            premium_subscription.daily_max_messages = 500
            premium_subscription.daily_max_tokens = 1000000
            premium_subscription.weekly_max_messages = 2000
            premium_subscription.weekly_max_tokens = 5000000
            premium_subscription.monthly_max_messages = 5000
            premium_subscription.monthly_max_tokens = 20000000
            premium_subscription.monthly_free_model_messages = 10000
            premium_subscription.monthly_free_model_tokens = 10000000
            premium_subscription.daily_image_generation_limit = 100
            premium_subscription.weekly_image_generation_limit = 500
            premium_subscription.monthly_image_generation_limit = 2000
            premium_subscription.is_active = True
            premium_subscription.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated {premium_subscription.name} subscription')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated subscription types and usage limits')
        )