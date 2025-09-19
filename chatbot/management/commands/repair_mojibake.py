from django.core.management.base import BaseCommand
from django.utils import timezone
from chatbot.models import ChatMessage

MOJIBAKE_MARKERS = [
    'Ù', 'Ø', 'Û', 'â', '€', '', '', ''
]

class Command(BaseCommand):
    help = "Repair mojibake (garbled UTF-8) content in ChatMessage records by re-decoding latin-1 to utf-8."

    def add_arguments(self, parser):
        parser.add_argument(
            '--since-hours', type=int, default=168,  # last 7 days
            help='Only attempt to repair messages created within the last N hours (default: 168 hours).'
        )
        parser.add_argument(
            '--dry-run', action='store_true', help='Only show changes without saving to DB.'
        )

    def handle(self, *args, **options):
        since_hours = options['since_hours']
        dry_run = options['dry_run']
        cutoff = timezone.now() - timezone.timedelta(hours=since_hours)

        qs = ChatMessage.objects.filter(created_at__gte=cutoff)
        total = qs.count()
        repaired = 0

        self.stdout.write(self.style.NOTICE(f"Scanning {total} messages since {since_hours} hours ago..."))

        for msg in qs.iterator():
            content = msg.content or ''
            if not content:
                continue

            # Heuristic: if mojibake markers appear, attempt repair
            if any(marker in content for marker in MOJIBAKE_MARKERS):
                try:
                    fixed = content.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore')
                except Exception:
                    continue

                if fixed and fixed != content:
                    repaired += 1
                    if dry_run:
                        self.stdout.write(f"Would repair message {msg.id}: '{content[:40]}...' -> '{fixed[:40]}...'")
                    else:
                        msg.content = fixed
                        msg.save(update_fields=['content'])
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry-run complete. {repaired} messages would be repaired."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Repair complete. {repaired} messages repaired."))
