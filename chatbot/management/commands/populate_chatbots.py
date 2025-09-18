from django.core.management.base import BaseCommand
from chatbot.models import Chatbot
from ai_models.models import AIModel
from subscriptions.models import SubscriptionType

class Command(BaseCommand):
    help = 'Populate initial chatbots'

    def handle(self, *args, **options):
        # Get AI models
        try:
            gpt4_model = AIModel.objects.get(model_id='openai/gpt-4-turbo')
            claude_model = AIModel.objects.get(model_id='anthropic/claude-3-opus')
            gemini_model = AIModel.objects.get(model_id='google/gemini-pro')
            dall_e_model = AIModel.objects.get(model_id='openai/dall-e-3')
        except AIModel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Required AI models not found. Please run populate_models first.')
            )
            return
        
        # Get subscription types
        try:
            basic_subscription = SubscriptionType.objects.get(name='Basic')
            premium_subscription = SubscriptionType.objects.get(name='Premium')
        except SubscriptionType.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Required subscription types not found. Please run populate_subscriptions first.')
            )
            return
        
        # Create chatbots
        chatbots_data = [
            {
                'name': 'General Assistant',
                'description': 'A general-purpose AI assistant for answering questions and helping with tasks',
                'subscription_types': [],
                'system_prompt': 'You are a helpful AI assistant. Answer questions clearly and concisely.',
            },
            {
                'name': 'Creative Writer',
                'description': 'An AI specialized in creative writing, storytelling, and content generation',
                'subscription_types': [basic_subscription, premium_subscription],
                'system_prompt': 'You are a creative writing assistant. Help users with storytelling, content creation, and creative tasks.',
            },
            {
                'name': 'Technical Expert',
                'description': 'An AI expert in technical topics, programming, and problem-solving',
                'subscription_types': [premium_subscription],
                'system_prompt': 'You are a technical expert assistant. Help users with programming, technical questions, and problem-solving.',
            },
            {
                'name': 'Image Generator',
                'description': 'An AI that can generate images from text descriptions',
                'subscription_types': [premium_subscription],
                'system_prompt': 'You are an image generation assistant. Create detailed image descriptions based on user requests. Only use image generation models for this chatbot.',
            }
        ]
        
        for chatbot_data in chatbots_data:
            subscription_types = chatbot_data.pop('subscription_types')
            
            # Create or get chatbot
            chatbot, created = Chatbot.objects.get_or_create(
                name=chatbot_data['name'],
                defaults=chatbot_data
            )
            
            if created:
                # Set subscription types
                chatbot.subscription_types.set(subscription_types)
                self.stdout.write(
                    self.style.SUCCESS(f'Created chatbot: {chatbot.name}')
                )
            else:
                self.stdout.write(
                    f'Already exists: {chatbot.name}'
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated chatbots')
        )