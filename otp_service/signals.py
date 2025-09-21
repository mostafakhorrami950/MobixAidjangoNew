from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import OTP

@receiver(post_migrate)
def create_otp_permissions(sender, **kwargs):
    """
    Create custom permissions for OTP model after migration
    """
    pass