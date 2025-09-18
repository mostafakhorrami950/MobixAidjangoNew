from django.core.management.base import BaseCommand, CommandError
from core.models import GlobalSettings

class Command(BaseCommand):
    help = 'Create or update default global settings'

    def handle(self, *args, **options):
        try:
            # Check if GlobalSettings already exists
            if GlobalSettings.objects.exists():
                settings = GlobalSettings.get_settings()
                self.stdout.write(
                    self.style.SUCCESS('GlobalSettings already exists with the following configuration:')
                )
                self.stdout.write(f'  Max file size: {settings.max_file_size_mb} MB')
                self.stdout.write(f'  Max files per message: {settings.max_files_per_message}')
                self.stdout.write(f'  Allowed extensions: {settings.allowed_file_extensions}')
                self.stdout.write(f'  Session timeout: {settings.session_timeout_hours} hours')
                self.stdout.write(f'  Messages per page: {settings.messages_per_page}')
                self.stdout.write(f'  API requests per minute: {settings.api_requests_per_minute}')
                return

            # Create default GlobalSettings
            settings = GlobalSettings.objects.create(
                max_file_size_mb=10,
                max_files_per_message=5,
                allowed_file_extensions="txt,pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,webp",
                session_timeout_hours=24,
                messages_per_page=50,
                api_requests_per_minute=60,
                is_active=True
            )

            self.stdout.write(
                self.style.SUCCESS('Successfully created default GlobalSettings!')
            )
            self.stdout.write(f'  Max file size: {settings.max_file_size_mb} MB')
            self.stdout.write(f'  Max files per message: {settings.max_files_per_message}')
            self.stdout.write(f'  Allowed extensions: {settings.allowed_file_extensions}')
            self.stdout.write(f'  Session timeout: {settings.session_timeout_hours} hours')
            self.stdout.write(f'  Messages per page: {settings.messages_per_page}')
            self.stdout.write(f'  API requests per minute: {settings.api_requests_per_minute}')

        except Exception as e:
            raise CommandError(f'Error creating GlobalSettings: {str(e)}')