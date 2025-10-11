from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Populate all initial data including AI models, chatbots, subscription types, etc.'

    def handle(self, *args, **options):
        # Import the populate_all_data_fixed script and run it
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        
        # Get models using apps.get_model
        AIModel = apps.get_model('ai_models', 'AIModel')
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        LimitationMessage = apps.get_model('chatbot', 'LimitationMessage')
        SidebarMenuItem = apps.get_model('chatbot', 'SidebarMenuItem')
        DefaultChatSettings = apps.get_model('chatbot', 'DefaultChatSettings')
        SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
        GlobalSettings = apps.get_model('core', 'GlobalSettings')
        TermsAndConditions = apps.get_model('core', 'TermsAndConditions')

        def populate_ai_models():
            """Populate initial AI models"""
            self.stdout.write("Populating AI models...")
            
            # Text generation models
            text_models = [
                {
                    'name': 'GPT-4 Turbo',
                    'model_id': 'openai/gpt-4-turbo',
                    'description': 'OpenAI GPT-4 Turbo model for advanced text generation',
                    'model_type': 'text',
                    'is_active': True,
                    'is_free': False,
                    'token_cost_multiplier': 1.00
                },
                {
                    'name': 'Claude 3 Opus',
                    'model_id': 'anthropic/claude-3-opus',
                    'description': 'Anthropic Claude 3 Opus model for advanced reasoning',
                    'model_type': 'text',
                    'is_active': True,
                    'is_free': False,
                    'token_cost_multiplier': 1.00
                },
                {
                    'name': 'Gemini Pro',
                    'model_id': 'google/gemini-pro',
                    'description': 'Google Gemini Pro model for balanced performance',
                    'model_type': 'text',
                    'is_active': True,
                    'is_free': True,  # مدل آزاد / رایگان
                    'token_cost_multiplier': 1.00
                },
                {
                    'name': 'GPT-3.5 Persian Lite',
                    'model_id': 'openai/gpt-3.5-persian-lite',
                    'description': 'نسخه سبک GPT-3.5 برای کاربران رایگان با محدودیت پایین',
                    'model_type': 'text',
                    'is_active': True,
                    'is_free': True,
                    'token_cost_multiplier': 0.50
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
                    'is_free': False,
                    'token_cost_multiplier': 1.00
                },
                {
                    'name': 'Stable Diffusion XL',
                    'model_id': 'stability-ai/stable-diffusion-xl',
                    'description': 'Stable Diffusion XL for fast image generation',
                    'model_type': 'image',
                    'is_active': True,
                    'is_free': False,
                    'token_cost_multiplier': 1.00
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
                        self.style.SUCCESS(f'  Created {model.name} ({model.model_id})')
                    )
                else:
                    self.stdout.write(
                        f'  Already exists: {model.name} ({model.model_id})'
                    )
            
            # Create image models
            for model_data in image_models:
                model, created = AIModel.objects.get_or_create(
                    model_id=model_data['model_id'],
                    defaults=model_data
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created {model.name} ({model.model_id})')
                    )
                else:
                    self.stdout.write(
                        f'  Already exists: {model.name} ({model.model_id})'
                    )
            
            self.stdout.write(
                self.style.SUCCESS('AI models populated successfully!\n')
            )


        def populate_subscription_types():
            """Populate initial subscription types"""
            self.stdout.write("Populating subscription types...")
            
            # Free subscription — محدود، تجربه اولیه
            free_subscription, created = SubscriptionType.objects.get_or_create(
                name='Free',
                defaults={
                    'description': 'پلن رایگان با دسترسی محدود',
                    'price': 0,
                    'duration_days': 30,
                    'sku': 'FREE_SUB_30D',
                    'max_tokens': 50000,
                    'max_tokens_free': 50000,
                    'max_openrouter_cost_usd': 0,
                    'hourly_max_messages': 2,
                    'hourly_max_tokens': 10000,
                    'three_hours_max_messages': 5,
                    'three_hours_max_tokens': 25000,
                    'twelve_hours_max_messages': 10,
                    'twelve_hours_max_tokens': 50000,
                    'daily_max_messages': 30,
                    'daily_max_tokens': 100000,
                    'weekly_max_messages': 150,
                    'weekly_max_tokens': 500000,
                    'monthly_max_messages': 500,
                    'monthly_max_tokens': 1000000,
                    'monthly_free_model_messages': 100,
                    'monthly_free_model_tokens': 200000,
                    'daily_image_generation_limit': 3,
                    'weekly_image_generation_limit': 15,
                    'monthly_image_generation_limit': 60,
                    'is_active': True
                }
            )
            if not created:
                free_subscription.description = 'پلن رایگان با دسترسی محدود'
                free_subscription.price = 0
                free_subscription.duration_days = 30
                free_subscription.sku = 'FREE_SUB_30D'
                free_subscription.max_tokens = 50000
                free_subscription.max_tokens_free = 50000
                free_subscription.max_openrouter_cost_usd = 0
                free_subscription.hourly_max_messages = 2
                free_subscription.hourly_max_tokens = 10000
                free_subscription.three_hours_max_messages = 5
                free_subscription.three_hours_max_tokens = 25000
                free_subscription.twelve_hours_max_messages = 10
                free_subscription.twelve_hours_max_tokens = 50000
                free_subscription.daily_max_messages = 30
                free_subscription.daily_max_tokens = 100000
                free_subscription.weekly_max_messages = 150
                free_subscription.weekly_max_tokens = 500000
                free_subscription.monthly_max_messages = 500
                free_subscription.monthly_max_tokens = 1000000
                free_subscription.monthly_free_model_messages = 100
                free_subscription.monthly_free_model_tokens = 200000
                free_subscription.daily_image_generation_limit = 3
                free_subscription.weekly_image_generation_limit = 15
                free_subscription.monthly_image_generation_limit = 60
                free_subscription.is_active = True
                free_subscription.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created {free_subscription.name} subscription'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  Updated {free_subscription.name} subscription'))
            
            # Basic (میانی)
            basic_subscription, created = SubscriptionType.objects.get_or_create(
                name='Basic',
                defaults={
                    'description': 'پلن پایه با امکانات بیشتر از رایگان',
                    'price': 70000,
                    'duration_days': 30,
                    'sku': 'BASIC_SUB_30D',
                    'max_tokens': 300000,
                    'max_tokens_free': 0,
                    'max_openrouter_cost_usd': 0,
                    'hourly_max_messages': 5,
                    'hourly_max_tokens': 30000,
                    'three_hours_max_messages': 15,
                    'three_hours_max_tokens': 90000,
                    'twelve_hours_max_messages': 30,
                    'twelve_hours_max_tokens': 180000,
                    'daily_max_messages': 120,
                    'daily_max_tokens': 400000,
                    'weekly_max_messages': 600,
                    'weekly_max_tokens': 2000000,
                    'monthly_max_messages': 2000,
                    'monthly_max_tokens': 8000000,
                    'monthly_free_model_messages': 500,
                    'monthly_free_model_tokens': 2000000,
                    'daily_image_generation_limit': 10,
                    'weekly_image_generation_limit': 50,
                    'monthly_image_generation_limit': 200,
                    'is_active': True
                }
            )
            if not created:
                basic_subscription.description = 'پلن پایه با امکانات بیشتر از رایگان'
                basic_subscription.price = 70000
                basic_subscription.duration_days = 30
                basic_subscription.sku = 'BASIC_SUB_30D'
                basic_subscription.max_tokens = 300000
                basic_subscription.max_tokens_free = 0
                basic_subscription.max_openrouter_cost_usd = 0
                basic_subscription.hourly_max_messages = 5
                basic_subscription.hourly_max_tokens = 30000
                basic_subscription.three_hours_max_messages = 15
                basic_subscription.three_hours_max_tokens = 90000
                basic_subscription.twelve_hours_max_messages = 30
                basic_subscription.twelve_hours_max_tokens = 180000
                basic_subscription.daily_max_messages = 120
                basic_subscription.daily_max_tokens = 400000
                basic_subscription.weekly_max_messages = 600
                basic_subscription.weekly_max_tokens = 2000000
                basic_subscription.monthly_max_messages = 2000
                basic_subscription.monthly_max_tokens = 8000000
                basic_subscription.monthly_free_model_messages = 500
                basic_subscription.monthly_free_model_tokens = 2000000
                basic_subscription.daily_image_generation_limit = 10
                basic_subscription.weekly_image_generation_limit = 50
                basic_subscription.monthly_image_generation_limit = 200
                basic_subscription.is_active = True
                basic_subscription.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created {basic_subscription.name} subscription'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  Updated {basic_subscription.name} subscription'))
            
            # Premium subscription — دسترسی کامل‌تر
            premium_subscription, created = SubscriptionType.objects.get_or_create(
                name='Premium',
                defaults={
                    'description': 'پلن حرفه‌ای با دسترسی کامل',
                    'price': 200000,
                    'duration_days': 30,
                    'sku': 'PREMIUM_SUB_30D',
                    'max_tokens': 0,  # ۰ = نامحدود
                    'max_tokens_free': 0,
                    'max_openrouter_cost_usd': 0,
                    'hourly_max_messages': 20,
                    'hourly_max_tokens': 200000,
                    'three_hours_max_messages': 60,
                    'three_hours_max_tokens': 600000,
                    'twelve_hours_max_messages': 150,
                    'twelve_hours_max_tokens': 1500000,
                    'daily_max_messages': 500,
                    'daily_max_tokens': 5000000,
                    'weekly_max_messages': 2000,
                    'weekly_max_tokens': 20000000,
                    'monthly_max_messages': 6000,
                    'monthly_max_tokens': 100000000,
                    'monthly_free_model_messages': 2000,
                    'monthly_free_model_tokens': 10000000,
                    'daily_image_generation_limit': 30,
                    'weekly_image_generation_limit': 150,
                    'monthly_image_generation_limit': 600,
                    'is_active': True
                }
            )
            if not created:
                premium_subscription.description = 'پلن حرفه‌ای با دسترسی کامل'
                premium_subscription.price = 200000
                premium_subscription.duration_days = 30
                premium_subscription.sku = 'PREMIUM_SUB_30D'
                premium_subscription.max_tokens = 0
                premium_subscription.max_tokens_free = 0
                premium_subscription.max_openrouter_cost_usd = 0
                premium_subscription.hourly_max_messages = 20
                premium_subscription.hourly_max_tokens = 200000
                premium_subscription.three_hours_max_messages = 60
                premium_subscription.three_hours_max_tokens = 600000
                premium_subscription.twelve_hours_max_messages = 150
                premium_subscription.twelve_hours_max_tokens = 1500000
                premium_subscription.daily_max_messages = 500
                premium_subscription.daily_max_tokens = 5000000
                premium_subscription.weekly_max_messages = 2000
                premium_subscription.weekly_max_tokens = 20000000
                premium_subscription.monthly_max_messages = 6000
                premium_subscription.monthly_max_tokens = 100000000
                premium_subscription.monthly_free_model_messages = 2000
                premium_subscription.monthly_free_model_tokens = 10000000
                premium_subscription.daily_image_generation_limit = 30
                premium_subscription.weekly_image_generation_limit = 150
                premium_subscription.monthly_image_generation_limit = 600
                premium_subscription.is_active = True
                premium_subscription.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created {premium_subscription.name} subscription'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  Updated {premium_subscription.name} subscription'))
            
            self.stdout.write(self.style.SUCCESS('Subscription types populated successfully!\n'))

        def populate_chatbots():
            """Populate initial chatbots"""
            self.stdout.write("Populating chatbots...")
            
            # Get AI models
            try:
                gpt4_model = AIModel.objects.get(model_id='openai/gpt-4-turbo')
                claude_model = AIModel.objects.get(model_id='anthropic/claude-3-opus')
                gemini_model = AIModel.objects.get(model_id='google/gemini-pro')
                dalle_model = AIModel.objects.get(model_id='openai/dall-e-3')
                lite_model = AIModel.objects.get(model_id='openai/gpt-3.5-persian-lite')
            except AIModel.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('  Error: Required AI models not found. Please run populate_ai_models first.')
                )
                return
            
            # Get subscription types
            try:
                free_subscription = SubscriptionType.objects.get(name='Free')
                basic_subscription = SubscriptionType.objects.get(name='Basic')
                premium_subscription = SubscriptionType.objects.get(name='Premium')
            except SubscriptionType.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('  Error: Required subscription types not found. Please run populate_subscriptions first.')
                )
                return
            
            # Create chatbots
            chatbots_data = [
                {
                    'name': 'General Assistant',
                    'description': 'A general-purpose AI assistant for answering questions and helping with tasks',
                    'subscription_types': [free_subscription, basic_subscription, premium_subscription],
                    'system_prompt': 'You are a helpful AI assistant. Answer questions clearly and concisely.',
                    'chatbot_type': 'text'
                },
                {
                    'name': 'Creative Writer',
                    'description': 'An AI specialized in creative writing, storytelling, and content generation',
                    'subscription_types': [basic_subscription, premium_subscription],
                    'system_prompt': 'You are a creative writing assistant. Help users with storytelling, content creation, and creative tasks.',
                    'chatbot_type': 'text'
                },
                {
                    'name': 'Technical Expert',
                    'description': 'An AI expert in technical topics, programming, and problem-solving',
                    'subscription_types': [premium_subscription],
                    'system_prompt': 'You are a technical expert assistant. Help users with programming, technical questions, and problem-solving.',
                    'chatbot_type': 'text'
                },
                {
                    'name': 'Image Generator',
                    'description': 'An AI that can generate images from text descriptions',
                    'subscription_types': [basic_subscription, premium_subscription],
                    'system_prompt': 'You are an image generation assistant. Create detailed image descriptions based on user requests. Only use image generation models for this chatbot.',
                    'chatbot_type': 'image'
                }
            ]
            
            for chatbot_data in chatbots_data:
                subscription_types = chatbot_data.pop('subscription_types')
                chatbot, created = Chatbot.objects.get_or_create(
                    name=chatbot_data['name'],
                    defaults=chatbot_data
                )
                if created:
                    chatbot.subscription_types.set(subscription_types)
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created chatbot: {chatbot.name}')
                    )
                else:
                    self.stdout.write(
                        f'  Already exists: {chatbot.name}'
                    )
            
            self.stdout.write(
                self.style.SUCCESS('Chatbots populated successfully!\n')
            )

        def populate_limitation_messages():
            """Populate default limitation messages"""
            self.stdout.write("Populating limitation messages...")
            
            default_messages = [
                {
                    'limitation_type': 'token_limit',
                    'title': 'محدودیت توکن',
                    'message': 'به سقف توکن مجاز رسیده‌اید. برای استفاده بیشتر اشتراک خود را ارتقاء دهید یا منتظر بازنشانی ماهانه بمانید.',
                },
                {
                    'limitation_type': 'message_limit',
                    'title': 'محدودیت پیام',
                    'message': 'شما به حد مجاز ارسال پیام در این بازه زمانی رسیده‌اید. برای ادامه، اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'daily_limit',
                    'title': 'محدودیت روزانه',
                    'message': 'شما از سقف مجاز روزانه استفاده کرده‌اید. لطفاً فردا دوباره تلاش کنید یا اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'weekly_limit',
                    'title': 'محدودیت هفتگی',
                    'message': 'شما به حد مجاز استفاده هفتگی رسیده‌اید. برای ادامه، اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'monthly_limit',
                    'title': 'محدودیت ماهانه',
                    'message': 'شما به حد مجاز استفاده ماهانه رسیده‌اید. برای ادامه، اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'file_upload_limit',
                    'title': 'محدودیت آپلود فایل',
                    'message': 'حد مجاز آپلود فایل‌ها را رد کرده‌اید. برای آپلود بیشتر، اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'image_generation_limit',
                    'title': 'محدودیت تولید تصویر',
                    'message': 'شما به سقف تولید تصویر رسیده‌اید. برای ادامه، اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'subscription_required',
                    'title': 'نیاز به اشتراک',
                    'message': 'برای استفاده از این امکان نیاز به اشتراک دارید. لطفاً یکی از بسته‌های اشتراک را خریداری کنید.',
                },
                {
                    'limitation_type': 'model_access_denied',
                    'title': 'عدم دسترسی به مدل',
                    'message': 'شما اجازه استفاده از این مدل هوش مصنوعی را ندارید. برای دسترسی بیشتر اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'general_limit',
                    'title': 'محدودیت کلی',
                    'message': 'شما به یکی از سقف‌های مجاز رسیده‌اید. لطفاً با پشتیبانی تماس بگیرید یا اشتراک خود را ارتقاء دهید.',
                },
                {
                    'limitation_type': 'openrouter_cost_limit',
                    'title': 'محدودیت هزینه OpenRouter',
                    'message': 'شما به سقف هزینه مجاز OpenRouter رسیده‌اید. برای ادامه، اشتراک خود را ارتقاء دهید.',
                },
            ]
            
            created_count = 0
            updated_count = 0
            
            for message_data in default_messages:
                limitation_message, created = LimitationMessage.objects.get_or_create(
                    limitation_type=message_data['limitation_type'],
                    defaults={
                        'title': message_data['title'],
                        'message': message_data['message'],
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created limitation message: {limitation_message.limitation_type}')
                    )
                else:
                    if (limitation_message.title != message_data['title'] or
                        limitation_message.message != message_data['message']):
                        limitation_message.title = message_data['title']
                        limitation_message.message = message_data['message']
                        limitation_message.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'  Updated limitation message: {limitation_message.limitation_type}')
                        )
            
            self.stdout.write(
                self.style.SUCCESS(f'Limitation messages populated successfully! Created: {created_count}, Updated: {updated_count}\n')
            )


        def populate_sidebar_menu_items():
            """Populate default sidebar menu items"""
            self.stdout.write("Populating sidebar menu items...")
            
            menu_items = [
                {
                    'name': 'چت جدید',
                    'url_name': 'chatbot:new_chat',
                    'icon_class': 'fas fa-plus',
                    'order': 1,
                    'is_active': True,
                    'required_permission': None,
                    'show_only_for_authenticated': True,
                    'show_only_for_non_authenticated': False,
                },
                {
                    'name': 'تاریخچه چت',
                    'url_name': 'chatbot:chat_history',
                    'icon_class': 'fas fa-history',
                    'order': 2,
                    'is_active': True,
                    'required_permission': None,
                    'show_only_for_authenticated': True,
                    'show_only_for_non_authenticated': False,
                },
                {
                    'name': 'مدل‌های هوش مصنوعی',
                    'url_name': 'ai_models:model_list',
                    'icon_class': 'fas fa-robot',
                    'order': 3,
                    'is_active': True,
                    'required_permission': None,
                    'show_only_for_authenticated': True,
                    'show_only_for_non_authenticated': False,
                },
                {
                    'name': 'اشتراک من',
                    'url_name': 'subscriptions:user_subscription',
                    'icon_class': 'fas fa-crown',
                    'order': 4,
                    'is_active': True,
                    'required_permission': None,
                    'show_only_for_authenticated': True,
                    'show_only_for_non_authenticated': False,
                },
                {
                    'name': 'خرید اشتراک',
                    'url_name': 'subscriptions:subscription_list',
                    'icon_class': 'fas fa-shopping-cart',
                    'order': 5,
                    'is_active': True,
                    'required_permission': None,
                    'show_only_for_authenticated': False,
                    'show_only_for_non_authenticated': True,
                },
                {
                    'name': 'ورود / ثبت نام',
                    'url_name': 'accounts:login',
                    'icon_class': 'fas fa-sign-in-alt',
                    'order': 6,
                    'is_active': True,
                    'required_permission': None,
                    'show_only_for_authenticated': False,
                    'show_only_for_non_authenticated': True,
                },
                {
                    'name': 'هزینه‌های استفاده',
                    'url_name': 'subscriptions:user_openrouter_costs',
                    'icon_class': 'fas fa-coins',
                    'order': 7,
                    'is_active': True,
                    'required_permission': None,
                    'show_only_for_authenticated': True,
                    'show_only_for_non_authenticated': False,
                },
            ]
            
            created_count = 0
            updated_count = 0
            
            for item_data in menu_items:
                menu_item, created = SidebarMenuItem.objects.get_or_create(
                    name=item_data['name'],
                    url_name=item_data['url_name'],
                    defaults=item_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created menu item: {menu_item.name}')
                    )
                else:
                    needs_update = False
                    for key, value in item_data.items():
                        if getattr(menu_item, key) != value:
                            setattr(menu_item, key, value)
                            needs_update = True
                    if needs_update:
                        menu_item.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'  Updated menu item: {menu_item.name}')
                        )
                    else:
                        self.stdout.write(
                            f'  Already exists: {menu_item.name}'
                        )
            
            self.stdout.write(
                self.style.SUCCESS(f'Sidebar menu items populated successfully! Created: {created_count}, Updated: {updated_count}\n')
            )

        def populate_global_settings():
            """Populate default global settings"""
            self.stdout.write("Populating global settings...")
            
            if GlobalSettings.objects.exists():
                settings = GlobalSettings.get_settings()
                self.stdout.write(f'  GlobalSettings already exists:')
                self.stdout.write(f'    Max file size: {settings.max_file_size_mb} MB')
                self.stdout.write(f'    Max files per message: {settings.max_files_per_message}')
                self.stdout.write(f'    Allowed extensions: {settings.allowed_file_extensions}')
                self.stdout.write(f'    Session timeout: {settings.session_timeout_hours} hours')
                self.stdout.write(f'    Messages per page: {settings.messages_per_page}')
                self.stdout.write(f'    API requests per minute: {settings.api_requests_per_minute}')
            else:
                settings = GlobalSettings.objects.create(
                    max_file_size_mb=10,
                    max_files_per_message=5,
                    allowed_file_extensions="txt,pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,webp",
                    session_timeout_hours=24,
                    messages_per_page=50,
                    api_requests_per_minute=60,
                    is_active=True
                )
                self.stdout.write(f'  Created default GlobalSettings:')
                self.stdout.write(f'    Max file size: {settings.max_file_size_mb} MB')
                self.stdout.write(f'    Max files per message: {settings.max_files_per_message}')
                self.stdout.write(f'    Allowed extensions: {settings.allowed_file_extensions}')
                self.stdout.write(f'    Session timeout: {settings.session_timeout_hours} hours')
                self.stdout.write(f'    Messages per page: {settings.messages_per_page}')
                self.stdout.write(f'    API requests per minute: {settings.api_requests_per_minute}')
            
            self.stdout.write(
                self.style.SUCCESS('Global settings populated successfully!\n')
            )

        def populate_terms_and_conditions():
            """Populate default terms and conditions"""
            self.stdout.write("Populating terms and conditions...")
            
            if TermsAndConditions.objects.filter(is_active=True).exists():
                terms = TermsAndConditions.get_active_terms()
                self.stdout.write(
                    f'  Active terms and conditions already exist: {terms.title}'
                )
            else:
                terms = TermsAndConditions.objects.create(
                    title="شرایط و قوانین استفاده",
                    content="شرایط و قوانین استفاده از سرویس در اینجا قرار خواهد گرفت.",
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  Created default terms and conditions: {terms.title}')
                )
            
            self.stdout.write(
                self.style.SUCCESS('Terms and conditions populated successfully!\n')
            )

        def populate_default_chat_settings():
            """Populate default chat settings"""
            self.stdout.write("Populating default chat settings...")
            
            try:
                gemini_model = AIModel.objects.get(model_id='google/gemini-pro')
                general_assistant = Chatbot.objects.get(name='General Assistant')
            except (AIModel.DoesNotExist, Chatbot.DoesNotExist):
                self.stdout.write(
                    self.style.ERROR('  Error: Required models not found. Please run populate_ai_models and populate_chatbots first.')
                )
                return
            
            if DefaultChatSettings.objects.filter(is_active=True).exists():
                default_settings = DefaultChatSettings.objects.filter(is_active=True).first()
                self.stdout.write(
                    f'  Active default chat settings already exist: {default_settings.name}'
                )
            else:
                default_settings = DefaultChatSettings.objects.create(
                    name="Default Chat Settings",
                    default_chatbot=general_assistant,
                    default_ai_model=gemini_model,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  Created default chat settings: {default_settings.name}')
                )
                self.stdout.write(
                    f'    Default chatbot: {default_settings.default_chatbot.name}'
                )
                self.stdout.write(
                    f'    Default AI model: {default_settings.default_ai_model.name}'
                )
            
            self.stdout.write(
                self.style.SUCCESS('Default chat settings populated successfully!\n')
            )

        # Main execution
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting comprehensive data population for MobixAI (Updated) ...')
        )
        self.stdout.write("=" * 60)
        
        try:
            populate_ai_models()
            populate_subscription_types()
            populate_chatbots()
            populate_limitation_messages()
            populate_sidebar_menu_items()
            populate_global_settings()
            populate_terms_and_conditions()
            populate_default_chat_settings()
            
            self.stdout.write("=" * 60)
            self.stdout.write(
                self.style.SUCCESS('🎉 All data populated successfully! (Updated) ')
            )
            self.stdout.write("\n📊 Summary:")
            self.stdout.write(f"  - AI Models: {AIModel.objects.count()}")
            self.stdout.write(f"  - Subscription Types: {SubscriptionType.objects.count()}")
            self.stdout.write(f"  - Chatbots: {Chatbot.objects.count()}")
            self.stdout.write(f"  - Limitation Messages: {LimitationMessage.objects.count()}")
            self.stdout.write(f"  - Sidebar Menu Items: {SidebarMenuItem.objects.count()}")
            self.stdout.write(f"  - Global Settings: {GlobalSettings.objects.count()}")
            self.stdout.write(f"  - Terms and Conditions: {TermsAndConditions.objects.count()}")
            self.stdout.write(f"  - Default Chat Settings: {DefaultChatSettings.objects.count()}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during data population: {e}')
            )
            import traceback
            traceback.print_exc()
