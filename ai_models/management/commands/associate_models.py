from django.core.management.base import BaseCommand
from ai_models.models import AIModel, ModelSubscription
from subscriptions.models import SubscriptionType

class Command(BaseCommand):
    help = 'Associate AI models with subscription types'

    def handle(self, *args, **options):
        # Get subscription types
        try:
            basic_subscription = SubscriptionType.objects.get(name='Basic')
            premium_subscription = SubscriptionType.objects.get(name='Premium')
        except SubscriptionType.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Basic or Premium subscription not found. Please run populate_subscriptions first.')
            )
            return
        
        # Get AI models
        text_models = AIModel.objects.filter(model_type='text')
        image_models = AIModel.objects.filter(model_type='image')
        
        # Associate text models
        for model in text_models:
            if model.is_free:
                # Free models are available to all users, no need to associate with subscriptions
                self.stdout.write(
                    f'Skipped association for free model: {model.name}'
                )
                continue
                
            # Associate with subscriptions
            model_subscription, created = ModelSubscription.objects.get_or_create(
                ai_model=model
            )
            
            if model.model_id == 'openai/gpt-4-turbo':
                # Only premium
                model_subscription.subscription_types.add(premium_subscription)
                self.stdout.write(
                    self.style.SUCCESS(f'Associated {model.name} with Premium subscription')
                )
            else:
                # Basic and Premium
                model_subscription.subscription_types.add(basic_subscription, premium_subscription)
                self.stdout.write(
                    self.style.SUCCESS(f'Associated {model.name} with Basic and Premium subscriptions')
                )
        
        # Associate image models
        for model in image_models:
            # Associate with subscriptions
            model_subscription, created = ModelSubscription.objects.get_or_create(
                ai_model=model
            )
            
            if model.model_id == 'openai/dall-e-3':
                # Only premium
                model_subscription.subscription_types.add(premium_subscription)
                self.stdout.write(
                    self.style.SUCCESS(f'Associated {model.name} with Premium subscription')
                )
            else:
                # Basic and Premium
                model_subscription.subscription_types.add(basic_subscription, premium_subscription)
                self.stdout.write(
                    self.style.SUCCESS(f'Associated {model.name} with Basic and Premium subscriptions')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully associated AI models with subscription types')
        )