from django.core.management.base import BaseCommand
from django.utils import timezone
from chatbot.models import ChatMessage
from datetime import timedelta
import re


class Command(BaseCommand):
    help = 'Fix UTF-8 encoding issues in chat messages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Preview changes without applying them',
        )
        parser.add_argument(
            '--days',
            type=int,
            dest='days',
            default=7,
            help='Number of days to look back for messages (default: 7)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_back = options['days']
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        self.stdout.write(f"Looking for messages created after {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Query messages that might have encoding issues
        messages = ChatMessage.objects.filter(
            created_at__gte=cutoff_date
        ).order_by('-created_at')
        
        self.stdout.write(f"Found {messages.count()} messages to check")
        
        fixed_count = 0
        
        for message in messages:
            original_content = message.content
            
            # Check if content has mojibake patterns
            if self.has_encoding_issues(original_content):
                try:
                    # Try to fix encoding by decoding as latin-1 and re-encoding as utf-8
                    fixed_content = original_content.encode('latin-1').decode('utf-8')
                    
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(f"Would fix message {message.id}:")
                        )
                        self.stdout.write(f"  Original: {original_content[:100]}...")
                        self.stdout.write(f"  Fixed:    {fixed_content[:100]}...")
                    else:
                        message.content = fixed_content
                        message.save(update_fields=['content'])
                        self.stdout.write(
                            self.style.SUCCESS(f"Fixed message {message.id}")
                        )
                    
                    fixed_count += 1
                    
                except (UnicodeEncodeError, UnicodeDecodeError):
                    # Skip if we can't fix the encoding
                    self.stdout.write(
                        self.style.ERROR(f"Could not fix encoding for message {message.id}")
                    )
                    continue
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"Dry run complete. Would fix {fixed_count} messages.")
            )
            self.stdout.write("Run without --dry-run to apply changes.")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully fixed {fixed_count} messages.")
            )

    def has_encoding_issues(self, text):
        """
        Check if text has common mojibake patterns
        """
        if not text:
            return False
            
        # Common mojibake patterns for Persian/Arabic text
        mojibake_patterns = [
            r'Ø§',  # آ encoded as latin-1
            r'Ù\u0088',  # و encoded as latin-1
            r'Ø¨',  # ب encoded as latin-1
            r'Ù\u0087',  # ه encoded as latin-1
            r'Ø±',  # ر encoded as latin-1
            r'Ø¯',  # د encoded as latin-1
            r'â€\u008e',  # RTL mark
            r'â€\u008f',  # LTR mark
        ]
        
        for pattern in mojibake_patterns:
            if re.search(pattern, text):
                return True
                
        # Check for other suspicious patterns
        # Look for sequences of question marks or replacement characters
        if '???' in text or '\ufffd' in text:
            return True
            
        return False