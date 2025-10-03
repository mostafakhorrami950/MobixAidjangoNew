from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import UserSubscription, SubscriptionType
from subscriptions.services import UsageService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check for expired subscriptions and reset usage counters'

    def handle(self, *args, **options):
        try:
            # Get all active subscriptions that have expired
            expired_subscriptions = UserSubscription.objects.filter(
                is_active=True,
                end_date__lt=timezone.now()
            )
            
            expired_count = 0
            for subscription in expired_subscriptions:
                # Deactivate the subscription
                subscription.is_active = False
                subscription.save()
                
                # Reset usage counters for this user
                UsageService.reset_user_usage(subscription.user, subscription.subscription_type)
                
                # ALSO reset chat session usage to ensure tokens are properly reset
                UsageService.reset_chat_session_usage(subscription.user, subscription.subscription_type)
                
                expired_count += 1
                logger.info(f"Expired subscription deactivated and usage reset for user {subscription.user.name}")
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully processed {expired_count} expired subscriptions')
            )
            
        except Exception as e:
            logger.error(f"Error checking expired subscriptions: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error checking expired subscriptions: {str(e)}')
            )