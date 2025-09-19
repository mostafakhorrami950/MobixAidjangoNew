"""
سرویس تولید عنوان خودکار برای چت‌ها
Chat Title Auto-Generation Service
"""
import logging
from django.apps import apps
from ai_models.services import OpenRouterService
from django.db.models import Q
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class ChatTitleService:
    """
    سرویس مسئول تولید عنوان خودکار برای جلسات چت بر اساس اولین پیام کاربر
    Service responsible for automatic title generation for chat sessions based on first user message
    """
    
    @staticmethod
    def should_generate_title(session) -> bool:
        """
        بررسی اینکه آیا برای این session باید عنوان تولید شود یا خیر
        Check if title should be generated for this session
        """
        try:
            # اگر session قبلاً عنوان سفارشی داشته، تولید نکن
            if session.title and session.title != 'چت جدید':
                return False
                
            # تعداد پیام‌های کاربر در این session را بشمار
            user_messages_count = session.messages.filter(
                message_type='user', 
                disabled=False
            ).count()
            
            # فقط برای اولین پیام کاربر عنوان تولید کن
            return user_messages_count == 1
            
        except Exception as e:
            logger.error(f"Error checking if should generate title: {str(e)}")
            return False
    
    @staticmethod
    def get_suitable_ai_model(user, session):
        """
        یافتن مناسب‌ترین مدل AI برای تولید عنوان
        Find the most suitable AI model for title generation
        """
        try:
            AIModel = apps.get_model('ai_models', 'AIModel')
            user_subscription = user.get_subscription_type()
            
            # ابتدا سعی کن از مدل session استفاده کنی
            if session.ai_model and session.ai_model.model_type == 'text':
                if user.has_access_to_model(session.ai_model):
                    return session.ai_model
            
            # در غیر این صورت مدل مناسب پیدا کن
            models_query = AIModel.objects.filter(
                is_active=True,
                model_type='text'
            )
            
            if user_subscription:
                # مدل‌های در دسترس کاربر را پیدا کن
                ai_model = models_query.filter(
                    Q(is_free=True) | Q(subscriptions__subscription_types=user_subscription)
                ).first()
            else:
                # اگر اشتراک نداره، فقط مدل‌های رایگان
                ai_model = models_query.filter(is_free=True).first()
            
            # اگر هیچ مدلی پیدا نشد، از اولین مدل فعال استفاده کن
            if not ai_model:
                ai_model = AIModel.objects.filter(
                    is_active=True,
                    model_type='text'
                ).first()
                
            return ai_model
            
        except Exception as e:
            logger.error(f"Error getting suitable AI model: {str(e)}")
            return None
    
    @staticmethod
    def generate_title_with_ai(first_message: str, ai_model) -> str:
        """
        تولید عنوان با استفاده از AI
        Generate title using AI
        """
        try:
            if not ai_model:
                return 'چت جدید'
                
            # پرامپت فارسی برای تولید عنوان بهتر
            prompt = f"""لطفاً برای این پیام یک عنوان کوتاه و توصیفی (حداکثر 5 کلمه) به زبان فارسی تولید کن:

"{first_message}"

فقط عنوان را بنویس، هیچ توضیح اضافی نیاز نیست."""
            
            openrouter_service = OpenRouterService()
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = openrouter_service.send_text_message(ai_model, messages)
            
            if isinstance(response, dict) and 'error' in response:
                logger.warning(f"AI title generation failed: {response['error']}")
                return ChatTitleService._generate_fallback_title(first_message)
            
            if isinstance(response, dict) and 'choices' in response:
                try:
                    choices = response.get('choices', [])
                    if choices and len(choices) > 0:
                        choice = choices[0]
                        if isinstance(choice, dict) and 'message' in choice:
                            message = choice['message']
                            if isinstance(message, dict) and 'content' in message:
                                content = message['content']
                                if content:
                                    title = content.strip()
                                    # حذف نقل‌قول‌ها و کاراکترهای اضافی
                                    title = title.replace('"', '').replace("'", "").strip()
                                    # محدود کردن طول عنوان
                                    if len(title) > 50:
                                        title = title[:50] + "..."
                                    return title if title else 'چت جدید'
                except (KeyError, IndexError, TypeError) as e:
                    logger.warning(f"Error parsing AI response: {str(e)}")
            
            return ChatTitleService._generate_fallback_title(first_message)
            
        except Exception as e:
            logger.error(f"Error generating title with AI: {str(e)}")
            return ChatTitleService._generate_fallback_title(first_message)
    
    @staticmethod
    def _generate_fallback_title(first_message: str) -> str:
        """
        تولید عنوان پیش‌فرض بر اساس محتوای پیام
        Generate fallback title based on message content
        """
        try:
            # پاک‌سازی پیام
            clean_message = first_message.strip()
            
            # اگر پیام خالی بود
            if not clean_message:
                return 'چت جدید'
            
            # کلمات کلیدی فارسی برای تشخیص نوع سوال
            question_words = ['چی', 'چه', 'کی', 'کجا', 'چرا', 'چطور', 'آیا', 'چگونه']
            code_words = ['کد', 'برنامه', 'function', 'def', 'class', 'import', 'if']
            help_words = ['کمک', 'راهنمایی', 'توضیح', 'یاد', 'یادم']
            
            # تبدیل به کلمات
            words = clean_message.split()[:5]  # فقط 5 کلمه اول
            
            # بررسی نوع سوال
            if any(word in clean_message.lower() for word in question_words):
                title_prefix = "سوال درباره "
            elif any(word in clean_message.lower() for word in code_words):
                title_prefix = "کمک برنامه‌نویسی "
            elif any(word in clean_message.lower() for word in help_words):
                title_prefix = "درخواست کمک "
            else:
                title_prefix = "گفتگو درباره "
            
            # ساخت عنوان از کلمات اول پیام
            main_words = ' '.join(words[:3])  # 3 کلمه اول
            title = title_prefix + main_words
            
            # محدود کردن طول
            if len(title) > 45:
                title = title[:45] + "..."
                
            return title
            
        except Exception as e:
            logger.error(f"Error generating fallback title: {str(e)}")
            return 'چت جدید'
    
    @staticmethod
    def generate_and_update_title(session, first_message: str, user) -> Tuple[bool, str]:
        """
        تولید و به‌روزرسانی عنوان چت
        Generate and update chat title
        
        Returns:
            Tuple[bool, str]: (success, title)
        """
        try:
            # بررسی اینکه آیا باید عنوان تولید شود
            if not ChatTitleService.should_generate_title(session):
                return False, session.title
            
            # پیدا کردن مدل مناسب
            ai_model = ChatTitleService.get_suitable_ai_model(user, session)
            
            # تولید عنوان
            new_title = ChatTitleService.generate_title_with_ai(first_message, ai_model)
            
            # به‌روزرسانی session
            session.title = new_title
            session.save(update_fields=['title'])
            
            logger.info(f"Auto-generated title for session {session.id}: {new_title}")
            return True, new_title
            
        except Exception as e:
            logger.error(f"Error generating and updating title: {str(e)}")
            return False, session.title
    
    @staticmethod
    async def generate_and_update_title_async(session, first_message: str, user) -> Tuple[bool, str]:
        """
        نسخه غیرهمزمان برای تولید و به‌روزرسانی عنوان
        Async version for generating and updating title
        """
        try:
            from django.db import transaction
            
            # اجرای عملیات در transaction جداگانه
            with transaction.atomic():
                return ChatTitleService.generate_and_update_title(session, first_message, user)
                
        except Exception as e:
            logger.error(f"Error in async title generation: {str(e)}")
            return False, session.title