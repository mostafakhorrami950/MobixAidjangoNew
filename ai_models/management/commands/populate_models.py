from django.core.management.base import BaseCommand
from ai_models.models import AIModel

class Command(BaseCommand):
    help = 'Populate initial AI models'

    def handle(self, *args, **options):
        # Text generation models
        text_models = [
            {
                'name': 'GPT-4 Turbo',
                'model_id': 'openai/gpt-4-turbo',
                'description': 'OpenAI GPT-4 Turbo model for advanced text generation',
                'model_type': 'text',
                'is_active': True,
                'is_free': False
            },
            {
                'name': 'Claude 3 Opus',
                'model_id': 'anthropic/claude-3-opus',
                'description': 'Anthropic Claude 3 Opus model for advanced reasoning',
                'model_type': 'text',
                'is_active': True,
                'is_free': False
            },
            {
                'name': 'Gemini Pro',
                'model_id': 'google/gemini-pro',
                'description': 'Google Gemini Pro model for balanced performance',
                'model_type': 'text',
                'is_active': True,
                'is_free': True  # Free model
            }
        ]
        
        # Image generation models
        image_models = [
            {
                'name': 'DALL-E 3',
                'model_id': 'openai/dall-e-3',
                'description': 'OpenAI DALL-E 3 for high-quality image generation',
                'model_type': 'image',
                'is_active': True,
                'is_free': False
            },
            {
                'name': 'Stable Diffusion XL',
                'model_id': 'stability-ai/stable-diffusion-xl',
                'description': 'Stable Diffusion XL for fast image generation',
                'model_type': 'image',
                'is_active': True,
                'is_free': False
            }
        ]
        
        # Create text models
        for model_data in text_models:
            model, created = AIModel.objects.get_or_create(
                model_id=model_data['model_id'],
                defaults=model_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {model.name} ({model.model_id})')
                )
            else:
                self.stdout.write(
                    f'Already exists: {model.name} ({model.model_id})'
                )
        
        # Create image models
        for model_data in image_models:
            model, created = AIModel.objects.get_or_create(
                model_id=model_data['model_id'],
                defaults=model_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {model.name} ({model.model_id})')
                )
            else:
                self.stdout.write(
                    f'Already exists: {model.name} ({model.model_id})'
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated AI models')
        )