from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionType

class Command(BaseCommand):
    help = 'Create a default free subscription type'

    def handle(self, *args, **options):
        # Create or update the free subscription
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
                'daily_max_messages': 50,
                'daily_max_tokens': 50000,
                'weekly_max_messages': 200,
                'weekly_max_tokens': 200000,
                'monthly_max_messages': 500,
                'monthly_max_tokens': 500000,
                'monthly_free_model_messages': 100,
                'monthly_free_model_tokens': 100000,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created Free subscription: {free_subscription.name}')
            )
        else:
            # Update the existing free subscription with default values
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
            free_subscription.daily_max_messages = 50
            free_subscription.daily_max_tokens = 50000
            free_subscription.weekly_max_messages = 200
            free_subscription.weekly_max_tokens = 200000
            free_subscription.monthly_max_messages = 500
            free_subscription.monthly_max_tokens = 500000
            free_subscription.monthly_free_model_messages = 100
            free_subscription.monthly_free_model_tokens = 100000
            free_subscription.is_active = True
            free_subscription.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated Free subscription: {free_subscription.name}')
            )