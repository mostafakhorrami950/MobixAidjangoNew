from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ModelArticle
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ModelArticle)
@receiver(post_delete, sender=ModelArticle)
def regenerate_sitemap(sender, **kwargs):
    """
    Regenerate the articles sitemap whenever an article is saved or deleted
    """
    try:
        # Note: With our new implementation, Django's sitemap view generates the sitemap dynamically
        # So we don't need to generate a static file anymore
        logger.info("Article changed - sitemap will be dynamically generated on next request")
    except Exception as e:
        # Log the error but don't fail the save operation
        logger.error(f"Error handling sitemap regeneration: {e}")