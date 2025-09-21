from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.services import UsageService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reset monthly free model usage limits for all users on the first day of each month'

    def handle(self, *args, **options):
        # Check if today is the first day of the month
        today = timezone.now()
        if today.day != 1:
            self.stdout.write(
                self.style.WARNING('Today is not the first day of the month. Skipping monthly usage reset.')
            )
            return

        try:
            # Use the new method to reset monthly free tokens
            # This method resets free model counters for all users without deleting data
            UsageService.reset_monthly_free_tokens()
            
            self.stdout.write(
                self.style.SUCCESS('Successfully reset monthly free model usage for all users')
            )
            
        except Exception as e:
            logger.error(f"Error resetting monthly usage: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error resetting monthly usage: {str(e)}')
            )