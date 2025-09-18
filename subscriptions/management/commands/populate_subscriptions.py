from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionType, UsageLimit

class Command(BaseCommand):
    help = 'Populate initial subscription types and usage limits'

    def handle(self, *args, **options):
        # Create subscription types
        basic_subscription, created = SubscriptionType.objects.get_or_create(
            name='Basic',
            defaults={
                'description': 'Basic subscription with limited access',
                'price': 9.99,
                'duration_days': 30,
                'sku': 'BASIC_SUB_30D',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {basic_subscription.name} subscription')
            )
        else:
            self.stdout.write(
                f'Already exists: {basic_subscription.name} subscription'
            )
        
        premium_subscription, created = SubscriptionType.objects.get_or_create(
            name='Premium',
            defaults={
                'description': 'Premium subscription with full access',
                'price': 29.99,
                'duration_days': 30,
                'sku': 'PREMIUM_SUB_30D',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created {premium_subscription.name} subscription')
            )
        else:
            self.stdout.write(
                f'Already exists: {premium_subscription.name} subscription'
            )
        
        # Create usage limits for Basic subscription
        basic_limits = [
            {'time_period': 'hourly', 'max_messages': 5, 'max_tokens': 5000, 'max_free_model_messages': 10, 'max_free_model_tokens': 10000},
            {'time_period': '3_hours', 'max_messages': 10, 'max_tokens': 10000, 'max_free_model_messages': 20, 'max_free_model_tokens': 20000},
            {'time_period': 'daily', 'max_messages': 20, 'max_tokens': 20000, 'max_free_model_messages': 50, 'max_free_model_tokens': 50000},
            {'time_period': 'weekly', 'max_messages': 100, 'max_tokens': 100000, 'max_free_model_messages': 200, 'max_free_model_tokens': 200000},
            {'time_period': 'monthly', 'max_messages': 300, 'max_tokens': 500000, 'max_free_model_messages': 500, 'max_free_model_tokens': 500000},
        ]
        
        for limit_data in basic_limits:
            limit, created = UsageLimit.objects.get_or_create(
                subscription_type=basic_subscription,
                time_period=limit_data['time_period'],
                defaults={
                    'max_messages': limit_data['max_messages'],
                    'max_tokens': limit_data['max_tokens'],
                    'max_free_model_messages': limit_data['max_free_model_messages'],
                    'max_free_model_tokens': limit_data['max_free_model_tokens']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {limit_data["time_period"]} limit for {basic_subscription.name}')
                )
            else:
                self.stdout.write(
                    f'Already exists: {limit_data["time_period"]} limit for {basic_subscription.name}'
                )
        
        # Create usage limits for Premium subscription
        premium_limits = [
            {'time_period': 'hourly', 'max_messages': 20, 'max_tokens': 20000, 'max_free_model_messages': 50, 'max_free_model_tokens': 50000},
            {'time_period': '3_hours', 'max_messages': 50, 'max_tokens': 100000, 'max_free_model_messages': 100, 'max_free_model_tokens': 100000},
            {'time_period': 'daily', 'max_messages': 500, 'max_tokens': 1000000, 'max_free_model_messages': 1000, 'max_free_model_tokens': 1000000},
            {'time_period': 'weekly', 'max_messages': 2000, 'max_tokens': 5000000, 'max_free_model_messages': 3000, 'max_free_model_tokens': 3000000},
            {'time_period': 'monthly', 'max_messages': 5000, 'max_tokens': 20000000, 'max_free_model_messages': 10000, 'max_free_model_tokens': 10000000},
        ]
        
        for limit_data in premium_limits:
            limit, created = UsageLimit.objects.get_or_create(
                subscription_type=premium_subscription,
                time_period=limit_data['time_period'],
                defaults={
                    'max_messages': limit_data['max_messages'],
                    'max_tokens': limit_data['max_tokens'],
                    'max_free_model_messages': limit_data['max_free_model_messages'],
                    'max_free_model_tokens': limit_data['max_free_model_tokens']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {limit_data["time_period"]} limit for {premium_subscription.name}')
                )
            else:
                self.stdout.write(
                    f'Already exists: {limit_data["time_period"]} limit for {premium_subscription.name}'
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated subscription types and usage limits')
        )