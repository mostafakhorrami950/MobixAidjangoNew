from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone

class CustomUserManager(UserManager):
    def create_user(self, phone_number, name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        if not name:
            raise ValueError('The Name must be set')
        
        user = self.model(phone_number=phone_number, name=name, **extra_fields)
        user.username = phone_number  # Set username to phone number
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, name, password, **extra_fields)

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} - {self.phone_number}"
    
    def save(self, *args, **kwargs):
        # Check if this is a new user
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # If this is a new user, assign them a free subscription
        if is_new:
            from subscriptions.models import SubscriptionType, UserSubscription
            try:
                # Get the free subscription type (Basic)
                free_subscription = SubscriptionType.objects.get(name='Basic')
                # Create user subscription
                UserSubscription.objects.create(
                    user=self,
                    subscription_type=free_subscription,
                    is_active=True,
                    start_date=timezone.now()
                )
            except SubscriptionType.DoesNotExist:
                # If Basic subscription doesn't exist, we'll handle this when the subscription is accessed
                pass
    
    def get_subscription_type(self):
        """
        Get the user's current subscription type
        """
        try:
            user_subscription = self.subscription
            if user_subscription.is_active:
                # Check if subscription has expired
                if user_subscription.end_date and user_subscription.end_date < timezone.now():
                    # Subscription has expired, deactivate it
                    user_subscription.is_active = False
                    user_subscription.save()
                    return None
                return user_subscription.subscription_type
        except:
            pass
        return None
    
    def get_subscription_info(self):
        """
        Get detailed subscription information including expiration date and usage
        """
        try:
            user_subscription = self.subscription
            if user_subscription.is_active:
                # Check if subscription has expired
                if user_subscription.end_date and user_subscription.end_date < timezone.now():
                    # Subscription has expired, deactivate it
                    user_subscription.is_active = False
                    user_subscription.save()
                    return None
                return user_subscription
        except:
            pass
        return None
    
    def has_access_to_model(self, ai_model):
        """
        Check if user has access to a specific AI model
        """
        # Free models are accessible to all registered users
        if ai_model.is_free:
            return True
            
        # Check if user has a subscription
        subscription_type = self.get_subscription_type()
        if not subscription_type:
            return False
            
        # Check if the model is available for this subscription type
        # The model can be accessed if it's linked to the user's subscription type through ModelSubscription
        try:
            # Check if there's a ModelSubscription that links this AI model to the user's subscription type
            from ai_models.models import ModelSubscription
            return ModelSubscription.objects.filter(
                ai_model=ai_model, 
                subscription_types=subscription_type
            ).exists()
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking model access: {str(e)}")
            return False