import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from chatbot.models import OpenRouterRequestCost
import datetime

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
        error_count = 0
        
        while offset < total_count:
            # Get a batch of records
            records = OpenRouterRequestCost.objects.all()[offset:offset + batch_size]
            
            for record in records:
                try:
                    # Try to access the datetime fields to see if they're valid
                    created_at = record.created_at
                    updated_at = record.updated_at
                    
                    # Check if datetimes are valid
                    if not isinstance(created_at, (datetime.datetime, type(None))) or \
                       not isinstance(updated_at, (datetime.datetime, type(None))):
                        # Fix invalid datetime values
                        self.stdout.write(f'Fixing invalid datetime for record ID {record.id}')
                        record.created_at = timezone.now()
                        record.updated_at = timezone.now()
                        record.save(update_fields=['created_at', 'updated_at'])
                        fixed_count += 1
                        
                except Exception as e:
                    # Handle any other errors
                    error_count += 1
                    self.stdout.write(f'Error processing record ID {record.id}: {str(e)}')
                    # Set to current time as fallback
                    try:
                        record.created_at = timezone.now()
                        record.updated_at = timezone.now()
                        record.save(update_fields=['created_at', 'updated_at'])
                        fixed_count += 1
                    except Exception as e2:
                        self.stdout.write(f'Failed to fix record ID {record.id}: {str(e2)}')
            
            offset += batch_size
            self.stdout.write(f'Processed {min(offset, total_count)}/{total_count} records...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully fixed {fixed_count} records with invalid datetime values. '
                f'Encountered {error_count} errors.'
            )
        )