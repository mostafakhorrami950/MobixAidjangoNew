from django.core.management.base import BaseCommand
from chatbot.models import FileUploadSettings
from subscriptions.models import SubscriptionType

class Command(BaseCommand):
    help = 'Setup file upload limits for all subscription types'

    def handle(self, *args, **options):
        # Get all subscription types
        subscription_types = SubscriptionType.objects.all()
        
        if not subscription_types.exists():
            self.stdout.write(
                'No subscription types found. Please create subscription types first.'
            )
            return

        # Define default limits for each subscription type
        limits_config = {
            'Free': {
                'max_file_size': 5 * 1024 * 1024,  # 5MB
                'allowed_extensions': 'jpg,jpeg,png,gif,pdf,txt',
                'max_files_per_chat': 3,
                'daily_file_limit': 5,
                'weekly_file_limit': 15,
                'monthly_file_limit': 30,
            },
            'Premium': {
                'max_file_size': 20 * 1024 * 1024,  # 20MB
                'allowed_extensions': 'jpg,jpeg,png,gif,pdf,txt,doc,docx,xls,xlsx,ppt,pptx',
                'max_files_per_chat': 10,
                'daily_file_limit': 20,
                'weekly_file_limit': 100,
                'monthly_file_limit': 300,
            }
        }

        # Create or update FileUploadSettings for each subscription type
        for subscription_type in subscription_types:
            # Get the configuration for this subscription type or use Free as default
            config = limits_config.get(subscription_type.name, limits_config['Free'])
            
            # Create or update the FileUploadSettings
            file_settings, created = FileUploadSettings.objects.update_or_create(
                subscription_type=subscription_type,
                defaults={
                    'max_file_size': config['max_file_size'],
                    'allowed_extensions': config['allowed_extensions'],
                    'max_files_per_chat': config['max_files_per_chat'],
                    'daily_file_limit': config['daily_file_limit'],
                    'weekly_file_limit': config['weekly_file_limit'],
                    'monthly_file_limit': config['monthly_file_limit'],
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(
                    f'Created file upload settings for {subscription_type.name}'
                )
            else:
                self.stdout.write(
                    f'Updated file upload settings for {subscription_type.name}'
                )

        self.stdout.write(
            'Successfully setup file upload limits for all subscription types'
        )