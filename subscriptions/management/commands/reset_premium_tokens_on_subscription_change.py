from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import UserSubscription, UserUsage
from subscriptions.services import UsageService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reset premium model tokens for users when their subscription is renewed, expired, or upgraded'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specific user ID to reset tokens for (optional)',
        )
        parser.add_argument(
            '--subscription-type-id',
            type=int,
            help='Specific subscription type ID to reset tokens for (optional)',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        subscription_type_id = options.get('subscription_type_id')
        
        try:
            # Get user subscriptions based on filters
            subscriptions = UserSubscription.objects.filter(is_active=True)
            
            if user_id:
                subscriptions = subscriptions.filter(user_id=user_id)
            
            if subscription_type_id:
                subscriptions = subscriptions.filter(subscription_type_id=subscription_type_id)
            
            reset_count = 0
            for user_subscription in subscriptions:
                # Reset premium tokens for this user and subscription type
                # This method resets counters without deleting data as requested
                UsageService.reset_user_usage(user_subscription.user, user_subscription.subscription_type)
                
                # ALSO reset chat session usage to ensure tokens are properly reset
                UsageService.reset_chat_session_usage(user_subscription.user, user_subscription.subscription_type)
                
                reset_count += 1
                
                self.stdout.write(
                    f'Reset premium tokens for user {user_subscription.user.name} '
                    f'with subscription {user_subscription.subscription_type.name}'
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully reset premium tokens for {reset_count} user subscriptions')
            )
            
        except Exception as e:
            logger.error(f"Error resetting premium tokens: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error resetting premium tokens: {str(e)}')
            )