import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from chatbot.models import OpenRouterRequestCost

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix invalid datetime values in OpenRouterRequestCost records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in each batch (default: 1000)',
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        self.stdout.write('Starting to fix OpenRouterRequestCost datetime records...')
        
        # Get total count
        total_count = OpenRouterRequestCost.objects.count()
        self.stdout.write(f'Total records to process: {total_count}')
        
        # Process in batches to avoid memory issues
        offset = 0
        fixed_count = 0
        
        while offset < total_count:
            # Get a batch of records
            records = OpenRouterRequestCost.objects.all()[offset:offset + batch_size]
            
            for record in records:
                try:
                    # Try to access the datetime fields to see if they're valid
                    _ = record.created_at
                    _ = record.updated_at
                except Exception as e:
                    # If there's an error, it means the datetime is invalid
                    self.stdout.write(f'Fixing invalid datetime for record ID {record.id}')
                    # Set to current time
                    record.created_at = timezone.now()
                    record.updated_at = timezone.now()
                    record.save()
                    fixed_count += 1
            
            offset += batch_size
            self.stdout.write(f'Processed {min(offset, total_count)}/{total_count} records...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully fixed {fixed_count} records with invalid datetime values'
            )
        )