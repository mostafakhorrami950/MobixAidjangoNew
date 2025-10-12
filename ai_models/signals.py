from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ModelArticle
from django.core.management import call_command

@receiver(post_save, sender=ModelArticle)
@receiver(post_delete, sender=ModelArticle)
def regenerate_sitemap(sender, **kwargs):
    """
    Regenerate the articles sitemap whenever an article is saved or deleted
    """
    try:
        call_command('generate_sitemap')
    except Exception as e:
        # Log the error but don't fail the save operation
        print(f"Error regenerating sitemap: {e}")