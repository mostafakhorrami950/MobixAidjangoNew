#!/usr/bin/env python
"""
Comprehensive data population script for MobixAI
This script populates all initial data including:
- AI Models
- Chatbots
- Subscription Types
- Limitation Messages
- Sidebar Menu Items
- Global Settings
- Default Chat Settings
- Terms and Conditions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import execute_from_command_line
from django.apps import apps

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
    print("Populating AI models...")
    
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
            'is_free': True,  # Free model
            'token_cost_multiplier': 1.00
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
            print(f"  Created {model.name} ({model.model_id})")
        else:
            print(f"  Already exists: {model.name} ({model.model_id})")
    
    # Create image models
    for model_data in image_models:
        model, created = AIModel.objects.get_or_create(
            model_id=model_data['model_id'],
            defaults=model_data
        )
        if created:
            print(f"  Created {model.name} ({model.model_id})")
        else:
            print(f"  Already exists: {model.name} ({model.model_id})")
    
    print("AI models populated successfully!\n")


def populate_subscription_types():
    """Populate initial subscription types"""
    print("Populating subscription types...")
    
    # Create subscription types
    free_subscription, created = SubscriptionType.objects.get_or_create(
        name='Free',
        defaults={
            'description': 'Free subscription with limited access',
            'price': 0,
            'duration_days': 30,
            'sku': 'FREE_SUB_30D',
            'max_tokens': 10000,
            'max_tokens_free': 0,
            'max_openrouter_cost_usd': 0,
            'hourly_max_messages': 5,
            'hourly_max_tokens': 5000,
            'three_hours_max_messages': 10,
            'three_hours_max_tokens': 10000,
            'twelve_hours_max_messages': 20,
            'twelve_hours_max_tokens': 20000,
            'daily_max_messages': 20,
            'daily_max_tokens': 20000,
            'weekly_max_messages': 100,
            'weekly_max_tokens': 100000,
            'monthly_max_messages': 300,
            'monthly_max_tokens': 500000,
            'monthly_free_model_messages': 500,
            'monthly_free_model_tokens': 500000,
            'daily_image_generation_limit': 10,
            'weekly_image_generation_limit': 50,
            'monthly_image_generation_limit': 200,
            'is_active': True
        }
    )
    if created:
        print(f"  Created {free_subscription.name} subscription")
    else:
        # Update existing Free subscription with correct values
        free_subscription.description = 'Free subscription with limited access'
        free_subscription.price = 0
        free_subscription.duration_days = 30
        free_subscription.sku = 'FREE_SUB_30D'
        free_subscription.max_tokens = 10000
        free_subscription.max_tokens_free = 0
        free_subscription.max_openrouter_cost_usd = 0
        free_subscription.hourly_max_messages = 5
        free_subscription.hourly_max_tokens = 5000
        free_subscription.three_hours_max_messages = 10
        free_subscription.three_hours_max_tokens = 10000
        free_subscription.twelve_hours_max_messages = 20
        free_subscription.twelve_hours_max_tokens = 20000
        free_subscription.daily_max_messages = 20
        free_subscription.daily_max_tokens = 20000
        free_subscription.weekly_max_messages = 100
        free_subscription.weekly_max_tokens = 100000
        free_subscription.monthly_max_messages = 300
        free_subscription.monthly_max_tokens = 500000
        free_subscription.monthly_free_model_messages = 500
        free_subscription.monthly_free_model_tokens = 500000
        free_subscription.daily_image_generation_limit = 10
        free_subscription.weekly_image_generation_limit = 50
        free_subscription.monthly_image_generation_limit = 200
        free_subscription.is_active = True
        free_subscription.save()
        print(f"  Updated {free_subscription.name} subscription")
    
    premium_subscription, created = SubscriptionType.objects.get_or_create(
        name='Premium',
        defaults={
            'description': 'Premium subscription with full access',
            'price': 29.99,
            'duration_days': 30,
            'sku': 'PREMIUM_SUB_30D',
            'max_tokens': 0,  # Unlimited
            'max_tokens_free': 0,
            'max_openrouter_cost_usd': 0,  # Unlimited
            'hourly_max_messages': 20,
            'hourly_max_tokens': 20000,
            'three_hours_max_messages': 50,
            'three_hours_max_tokens': 100000,
            'twelve_hours_max_messages': 200,
            'twelve_hours_max_tokens': 500000,
            'daily_max_messages': 500,
            'daily_max_tokens': 1000000,
            'weekly_max_messages': 2000,
            'weekly_max_tokens': 5000000,
            'monthly_max_messages': 5000,
            'monthly_max_tokens': 20000000,
            'monthly_free_model_messages': 10000,
            'monthly_free_model_tokens': 10000000,
            'daily_image_generation_limit': 100,
            'weekly_image_generation_limit': 500,
            'monthly_image_generation_limit': 2000,
            'is_active': True
        }
    )
    if created:
        print(f"  Created {premium_subscription.name} subscription")
    else:
        # Update existing Premium subscription with correct values
        premium_subscription.description = 'Premium subscription with full access'
        premium_subscription.price = 29.99
        premium_subscription.duration_days = 30
        premium_subscription.sku = 'PREMIUM_SUB_30D'
        premium_subscription.max_tokens = 0  # Unlimited
        premium_subscription.max_tokens_free = 0
        premium_subscription.max_openrouter_cost_usd = 0  # Unlimited
        premium_subscription.hourly_max_messages = 20
        premium_subscription.hourly_max_tokens = 20000
        premium_subscription.three_hours_max_messages = 50
        premium_subscription.three_hours_max_tokens = 100000
        premium_subscription.twelve_hours_max_messages = 200
        premium_subscription.twelve_hours_max_tokens = 500000
        premium_subscription.daily_max_messages = 500
        premium_subscription.daily_max_tokens = 1000000
        premium_subscription.weekly_max_messages = 2000
        premium_subscription.weekly_max_tokens = 5000000
        premium_subscription.monthly_max_messages = 5000
        premium_subscription.monthly_max_tokens = 20000000
        premium_subscription.monthly_free_model_messages = 10000
        premium_subscription.monthly_free_model_tokens = 10000000
        premium_subscription.daily_image_generation_limit = 100
        premium_subscription.weekly_image_generation_limit = 500
        premium_subscription.monthly_image_generation_limit = 2000
        premium_subscription.is_active = True
        premium_subscription.save()
        print(f"  Updated {premium_subscription.name} subscription")
    
    print("Subscription types populated successfully!\n")


def populate_chatbots():
    """Populate initial chatbots"""
    print("Populating chatbots...")
    
    # Get AI models
    try:
        gpt4_model = AIModel.objects.get(model_id='openai/gpt-4-turbo')
        claude_model = AIModel.objects.get(model_id='anthropic/claude-3-opus')
        gemini_model = AIModel.objects.get(model_id='google/gemini-pro')
        dall_e_model = AIModel.objects.get(model_id='openai/dall-e-3')
    except AIModel.DoesNotExist:
        print("  Error: Required AI models not found. Please run populate_ai_models first.")
        return
    
    # Get subscription types
    try:
        basic_subscription = SubscriptionType.objects.get(name='Free')
        premium_subscription = SubscriptionType.objects.get(name='Premium')
    except SubscriptionType.DoesNotExist:
        print("  Error: Required subscription types not found. Please run populate_subscriptions first.")
        return
    
    # Create chatbots
    chatbots_data = [
        {
            'name': 'General Assistant',
            'description': 'A general-purpose AI assistant for answering questions and helping with tasks',
            'subscription_types': [],
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
            'subscription_types': [premium_subscription],
            'system_prompt': 'You are an image generation assistant. Create detailed image descriptions based on user requests. Only use image generation models for this chatbot.',
            'chatbot_type': 'text'
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
            print(f"  Created chatbot: {chatbot.name}")
        else:
            print(f"  Already exists: {chatbot.name}")
    
    print("Chatbots populated successfully!\n")


def populate_limitation_messages():
    """Populate default limitation messages"""
    print("Populating limitation messages...")
    
    # Default limitation messages
    default_messages = [
        {
            'limitation_type': 'token_limit',
            'title': 'محدودیت توکن',
            'message': 'شما به حد مجاز استفاده از توکن‌ها رسیده‌اید. برای ادامه استفاده، اشتراک خود را ارتقاء دهید یا تا بازنشانی محدودیت صبر کنید.',
        },
        {
            'limitation_type': 'message_limit',
            'title': 'محدودیت پیام',
            'message': 'شما به حد مجاز تعداد پیام‌های روزانه رسیده‌اید. برای ارسال پیام‌های بیشتر، اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'daily_limit',
            'title': 'محدودیت روزانه',
            'message': 'شما به حد مجاز روزانه استفاده رسیده‌اید. لطفاً فردا دوباره تلاش کنید یا اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'weekly_limit',
            'title': 'محدودیت هفتگی',
            'message': 'شما به حد مجاز هفتگی استفاده رسیده‌اید. برای ادامه استفاده، اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'monthly_limit',
            'title': 'محدودیت ماهانه',
            'message': 'شما به حد مجاز ماهانه استفاده رسیده‌اید. برای ادامه استفاده، اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'file_upload_limit',
            'title': 'محدودیت آپلود فایل',
            'message': 'شما به حد مجاز آپلود فایل رسیده‌اید. برای آپلود فایل‌های بیشتر، اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'image_generation_limit',
            'title': 'محدودیت تولید تصویر',
            'message': 'شما به حد مجاز تولید تصویر رسیده‌اید. برای تولید تصویرهای بیشتر، اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'subscription_required',
            'title': 'نیاز به اشتراک',
            'message': 'برای استفاده از این قابلیت، نیاز به اشتراک دارید. لطفاً یکی از بسته‌های اشتراک ما را خریداری کنید.',
        },
        {
            'limitation_type': 'model_access_denied',
            'title': 'عدم دسترسی به مدل',
            'message': 'شما دسترسی لازم به این مدل هوش مصنوعی را ندارید. برای دسترسی، اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'general_limit',
            'title': 'محدودیت عمومی',
            'message': 'شما به حد مجاز استفاده رسیده‌اید. لطفاً با پشتیبانی تماس بگیرید یا اشتراک خود را ارتقاء دهید.',
        },
        {
            'limitation_type': 'openrouter_cost_limit',
            'title': 'محدودیت هزینه OpenRouter',
            'message': 'شما به حد مجاز هزینه OpenRouter رسیده‌اید. برای ادامه استفاده، اشتراک خود را ارتقاء دهید.',
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
            print(f"  Created limitation message: {limitation_message.limitation_type}")
        else:
            # Update existing message if needed
            if (limitation_message.title != message_data['title'] or
                limitation_message.message != message_data['message']):
                limitation_message.title = message_data['title']
                limitation_message.message = message_data['message']
                limitation_message.save()
                updated_count += 1
                print(f"  Updated limitation message: {limitation_message.limitation_type}")
    
    print(f"Limitation messages populated successfully! Created: {created_count}, Updated: {updated_count}\n")


def populate_sidebar_menu_items():
    """Populate default sidebar menu items"""
    print("Populating sidebar menu items...")
    
    # Default sidebar menu items
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
            print(f"  Created menu item: {menu_item.name}")
        else:
            # Update existing menu item if needed
            needs_update = False
            for key, value in item_data.items():
                if getattr(menu_item, key) != value:
                    setattr(menu_item, key, value)
                    needs_update = True
            
            if needs_update:
                menu_item.save()
                updated_count += 1
                print(f"  Updated menu item: {menu_item.name}")
            else:
                print(f"  Already exists: {menu_item.name}")
    
    print(f"Sidebar menu items populated successfully! Created: {created_count}, Updated: {updated_count}\n")


def populate_global_settings():
    """Populate default global settings"""
    print("Populating global settings...")
    
    # Check if GlobalSettings already exists
    if GlobalSettings.objects.exists():
        settings = GlobalSettings.get_settings()
        print(f"  GlobalSettings already exists:")
        print(f"    Max file size: {settings.max_file_size_mb} MB")
        print(f"    Max files per message: {settings.max_files_per_message}")
        print(f"    Allowed extensions: {settings.allowed_file_extensions}")
        print(f"    Session timeout: {settings.session_timeout_hours} hours")
        print(f"    Messages per page: {settings.messages_per_page}")
        print(f"    API requests per minute: {settings.api_requests_per_minute}")
    else:
        # Create default GlobalSettings
        settings = GlobalSettings.objects.create(
            max_file_size_mb=10,
            max_files_per_message=5,
            allowed_file_extensions="txt,pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,webp",
            session_timeout_hours=24,
            messages_per_page=50,
            api_requests_per_minute=60,
            is_active=True
        )
        
        print(f"  Created default GlobalSettings:")
        print(f"    Max file size: {settings.max_file_size_mb} MB")
        print(f"    Max files per message: {settings.max_files_per_message}")
        print(f"    Allowed extensions: {settings.allowed_file_extensions}")
        print(f"    Session timeout: {settings.session_timeout_hours} hours")
        print(f"    Messages per page: {settings.messages_per_page}")
        print(f"    API requests per minute: {settings.api_requests_per_minute}")
    
    print("Global settings populated successfully!\n")


def populate_terms_and_conditions():
    """Populate default terms and conditions"""
    print("Populating terms and conditions...")
    
    # Check if TermsAndConditions already exists
    if TermsAndConditions.objects.filter(is_active=True).exists():
        terms = TermsAndConditions.get_active_terms()
        print(f"  Active terms and conditions already exist: {terms.title}")
    else:
        # Create default TermsAndConditions
        terms = TermsAndConditions.objects.create(
            title="شرایط و قوانین استفاده",
            content="شرایط و قوانین استفاده از سرویس در اینجا قرار خواهد گرفت.",
            is_active=True
        )
        print(f"  Created default terms and conditions: {terms.title}")
    
    print("Terms and conditions populated successfully!\n")


def populate_default_chat_settings():
    """Populate default chat settings"""
    print("Populating default chat settings...")
    
    # Get required models
    try:
        gemini_model = AIModel.objects.get(model_id='google/gemini-pro')
        general_assistant = Chatbot.objects.get(name='General Assistant')
    except (AIModel.DoesNotExist, Chatbot.DoesNotExist):
        print("  Error: Required models not found. Please run populate_ai_models and populate_chatbots first.")
        return
    
    # Check if DefaultChatSettings already exists
    if DefaultChatSettings.objects.filter(is_active=True).exists():
        default_settings = DefaultChatSettings.objects.filter(is_active=True).first()
        print(f"  Active default chat settings already exist: {default_settings.name}")
    else:
        # Create default DefaultChatSettings
        default_settings = DefaultChatSettings.objects.create(
            name="Default Chat Settings",
            default_chatbot=general_assistant,
            default_ai_model=gemini_model,
            is_active=True
        )
        print(f"  Created default chat settings: {default_settings.name}")
        print(f"    Default chatbot: {default_settings.default_chatbot.name}")
        print(f"    Default AI model: {default_settings.default_ai_model.name}")
    
    print("Default chat settings populated successfully!\n")


def main():
    """Main function to populate all data"""
    print("🚀 Starting comprehensive data population for MobixAI...")
    print("=" * 60)
    
    try:
        # Populate data in order of dependencies
        populate_ai_models()
        populate_subscription_types()
        populate_chatbots()
        populate_limitation_messages()
        populate_sidebar_menu_items()
        populate_global_settings()
        populate_terms_and_conditions()
        populate_default_chat_settings()
        
        print("=" * 60)
        print("🎉 All data populated successfully!")
        print("\n📊 Summary:")
        print(f"  - AI Models: {AIModel.objects.count()}")
        print(f"  - Subscription Types: {SubscriptionType.objects.count()}")
        print(f"  - Chatbots: {Chatbot.objects.count()}")
        print(f"  - Limitation Messages: {LimitationMessage.objects.count()}")
        print(f"  - Sidebar Menu Items: {SidebarMenuItem.objects.count()}")
        print(f"  - Global Settings: {GlobalSettings.objects.count()}")
        print(f"  - Terms and Conditions: {TermsAndConditions.objects.count()}")
        print(f"  - Default Chat Settings: {DefaultChatSettings.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error during data population: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()