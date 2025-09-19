"""
Service for handling limitation messages
"""
from django.apps import apps


class LimitationMessageService:
    """
    Service to handle limitation messages for various user limits
    """
    
    @staticmethod
    def get_limitation_message(limitation_type, default_message=None):
        """
        Get the configured limitation message for a specific type
        
        Args:
            limitation_type (str): Type of limitation
            default_message (str): Default message if none configured
        
        Returns:
            dict: Message data with title and content
        """
        try:
            LimitationMessage = apps.get_model('chatbot', 'LimitationMessage')
            limitation_msg = LimitationMessage.objects.filter(
                limitation_type=limitation_type,
                is_active=True
            ).first()
            
            if limitation_msg:
                return {
                    'title': limitation_msg.title,
                    'message': limitation_msg.message
                }
            
        except Exception:
            pass
        
        # Return default message if no configured message found
        return {
            'title': 'محدودیت دسترسی',
            'message': default_message or 'شما به حد مجاز دسترسی رسیده‌اید. لطفاً با پشتیبانی تماس بگیرید.'
        }
    
    @staticmethod
    def get_token_limit_message():
        """Get message for token limit reached"""
        return LimitationMessageService.get_limitation_message(
            'token_limit',
            'شما به حد مجاز استفاده از توکن‌ها رسیده‌اید. برای ادامه استفاده، اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_message_limit_message():
        """Get message for message limit reached"""
        return LimitationMessageService.get_limitation_message(
            'message_limit',
            'شما به حد مجاز تعداد پیام‌ها رسیده‌اید. برای ارسال پیام‌های بیشتر، اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_daily_limit_message():
        """Get message for daily limit reached"""
        return LimitationMessageService.get_limitation_message(
            'daily_limit',
            'شما به حد مجاز روزانه استفاده رسیده‌اید. لطفاً فردا دوباره تلاش کنید یا اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_weekly_limit_message():
        """Get message for weekly limit reached"""
        return LimitationMessageService.get_limitation_message(
            'weekly_limit',
            'شما به حد مجاز هفتگی استفاده رسیده‌اید. برای ادامه استفاده، اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_monthly_limit_message():
        """Get message for monthly limit reached"""
        return LimitationMessageService.get_limitation_message(
            'monthly_limit',
            'شما به حد مجاز ماهانه استفاده رسیده‌اید. برای ادامه استفاده، اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_file_upload_limit_message():
        """Get message for file upload limit reached"""
        return LimitationMessageService.get_limitation_message(
            'file_upload_limit',
            'شما به حد مجاز آپلود فایل رسیده‌اید. برای آپلود فایل‌های بیشتر، اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_image_generation_limit_message():
        """Get message for image generation limit reached"""
        return LimitationMessageService.get_limitation_message(
            'image_generation_limit',
            'شما به حد مجاز تولید تصویر رسیده‌اید. برای تولید تصویرهای بیشتر، اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_subscription_required_message():
        """Get message for subscription required"""
        return LimitationMessageService.get_limitation_message(
            'subscription_required',
            'برای استفاده از این قابلیت، نیاز به اشتراک دارید. لطفاً یکی از بسته‌های اشتراک را خریداری کنید.'
        )
    
    @staticmethod
    def get_model_access_denied_message():
        """Get message for model access denied"""
        return LimitationMessageService.get_limitation_message(
            'model_access_denied',
            'شما دسترسی لازم به این مدل هوش مصنوعی را ندارید. برای دسترسی، اشتراک خود را ارتقاء دهید.'
        )
    
    @staticmethod
    def get_general_limit_message():
        """Get message for general limit reached"""
        return LimitationMessageService.get_limitation_message(
            'general_limit',
            'شما به حد مجاز استفاده رسیده‌اید. لطفاً با پشتیبانی تماس بگیرید.'
        )