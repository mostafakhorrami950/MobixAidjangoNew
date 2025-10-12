from django.db import migrations
from django.utils import timezone
import datetime

def fix_invalid_datetime_values(apps, schema_editor):
    """
    Fix any existing OpenRouterRequestCost records with invalid datetime values
    """
    OpenRouterRequestCost = apps.get_model('chatbot', 'OpenRouterRequestCost')
    
    # Get current valid datetime
    valid_datetime = timezone.now()
    
    # Find and fix records with invalid datetime values
    for record in OpenRouterRequestCost.objects.all():
        try:
            # Try to access the datetime fields
            _ = record.created_at
            _ = record.updated_at
        except Exception:
            # If there's an error, fix the datetime values
            record.created_at = valid_datetime
            record.updated_at = valid_datetime
            record.save(update_fields=['created_at', 'updated_at'])

def reverse_fix_invalid_datetime_values(apps, schema_editor):
    """
    Reverse function - no need to do anything
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0040_fix_openrouter_datetime_fields'),
    ]

    operations = [
        migrations.RunPython(
            fix_invalid_datetime_values,
            reverse_fix_invalid_datetime_values
        ),
    ]