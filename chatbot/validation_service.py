"""
Service for comprehensive validation of user limitations before message processing
"""
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from subscriptions.services import UsageService
from .limitation_service import LimitationMessageService
from .file_services import FileUploadService, GlobalFileService

logger = logging.getLogger(__name__)


class MessageValidationService:
    """
    Service to validate all user limitations before processing messages
    """
    
    @staticmethod
    def validate_all_limits(user, session, ai_model=None, uploaded_files=None, generate_image=False):
        """
        Comprehensive validation of all user limitations before message processing
        
        Args:
            user: User object
            session: ChatSession object
            ai_model: AIModel object (optional, will use session.ai_model if not provided)
            uploaded_files: List of uploaded files (optional)
            generate_image: Boolean indicating if image generation is requested
            
        Returns:
            tuple: (is_valid, error_message, error_code)
                - is_valid: Boolean indicating if all validations passed
                - error_message: String with human-readable error message
                - error_code: HTTP status code (429 for rate limits, 403 for access restrictions)
        """
        logger.info(f"Starting comprehensive validation for user {user.id}, session {session.id}")
        
        # Get subscription type
        subscription_type = user.get_subscription_type()
        if not subscription_type:
            limitation_msg = LimitationMessageService.get_subscription_required_message()
            return False, limitation_msg['message'], 403
        
        # Use session's AI model if not provided
        if not ai_model:
            ai_model = session.ai_model
            if not ai_model:
                return False, "هیچ مدل هوش مصنوعی با این جلسه مرتبط نیست", 500
        
        # Check user access to AI model
        if not user.has_access_to_model(ai_model):
            limitation_msg = LimitationMessageService.get_model_access_denied_message()
            return False, limitation_msg['message'], 403
        
        # Perform comprehensive usage limit checking (same as in views.py)
        if subscription_type:
            within_limit, message = UsageService.comprehensive_check(
                user, ai_model, subscription_type
            )
            if not within_limit:
                limitation_msg = LimitationMessageService.get_token_limit_message()
                return False, limitation_msg['message'], 429
        
        # Check image generation limits if requested
        if generate_image and subscription_type:
            within_limit, message = UsageService.check_image_generation_limit(
                user, subscription_type
            )
            if not within_limit:
                limitation_msg = LimitationMessageService.get_image_generation_limit_message()
                return False, limitation_msg['message'], 429
        
        # Check OpenRouter cost limits
        if subscription_type:
            within_limit, message = UsageService.check_openrouter_cost_limit(
                user, subscription_type, 0.0
            )
            if not within_limit:
                limitation_msg = LimitationMessageService.get_openrouter_cost_limit_message()
                return False, limitation_msg['message'], 429
        
        # Check file upload limits if files are being uploaded
        if uploaded_files and subscription_type:
            # Validate global file settings first
            files_valid, files_message = GlobalFileService.validate_files(uploaded_files)
            if not files_valid:
                return False, files_message, 403
            
            # Check subscription-based file upload limits for each file
            for uploaded_file in uploaded_files:
                # Check file upload limit
                within_limit, message = FileUploadService.check_file_upload_limit(
                    user, subscription_type, session
                )
                if not within_limit:
                    limitation_msg = LimitationMessageService.get_file_upload_limit_message()
                    return False, limitation_msg['message'], 429
                
                # Check file size limit
                within_limit, message = FileUploadService.check_file_size_limit(
                    subscription_type, uploaded_file.size
                )
                if not within_limit:
                    return False, f"فایل '{uploaded_file.name}': {message}", 403
                
                # Check file extension
                file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else ''
                if file_extension and not FileUploadService.check_file_extension_allowed(
                    subscription_type, file_extension
                ):
                    return False, f"فرمت فایل {file_extension} در '{uploaded_file.name}' مجاز نیست", 403
        
        logger.info("All validations passed successfully")
        return True, "", 200
    
    @staticmethod
    def validate_discount_code_usage(user, discount_code):
        """
        Validation for discount code usage limits
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            DiscountCode = apps.get_model('subscriptions', 'DiscountCode')
            DiscountUse = apps.get_model('subscriptions', 'DiscountUse')
            
            # Check if discount code exists and is active
            try:
                discount = DiscountCode.objects.get(code=discount_code, is_active=True)
            except DiscountCode.DoesNotExist:
                return False, "کد تخفیف معتبر نیست"
            
            # Check if discount code is expired
            if discount.is_expired:
                return False, "کد تخفیف منقضی شده است"
            
            # Check if discount code has reached maximum usage
            if discount.max_uses and discount.uses_count >= discount.max_uses:
                return False, "کد تخفیف به حداکثر استفاده رسیده است"
            
            # Check if user has reached maximum usage for this discount code
            user_uses = DiscountUse.objects.filter(user=user, discount_code=discount).count()
            if discount.max_uses_per_user and user_uses >= discount.max_uses_per_user:
                return False, "شما به حداکثر استفاده از این کد تخفیف رسیده‌اید"
            
            return True, ""
        except Exception as e:
            logger.error(f"Error validating discount code: {str(e)}")
            return False, "خطا در اعتبارسنجی کد تخفیف"
    
    @staticmethod
    def validate_subscription_upgrade(user, new_subscription):
        """
        Validation for subscription upgrade requests
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check if user has an active subscription
            current_subscription = user.get_subscription_type()
            if not current_subscription:
                return False, "شما اشتراک فعالی ندارید"
            
            # Check if new subscription is active
            if not new_subscription.is_active:
                return False, "اشتراک انتخابی فعال نیست"
            
            # Check if new subscription price is valid
            if new_subscription.price <= 0:
                return False, "اشتراک انتخابی قیمت معتبری ندارد"
            
            return True, ""
        except Exception as e:
            logger.error(f"Error validating subscription upgrade: {str(e)}")
            return False, "خطا در اعتبارسنجی ارتقاء اشتراک"
    
    @staticmethod
    def _check_hourly_message_limit(user, subscription_type):
        """
        Check hourly message sending limits per user
        
        Returns:
            tuple: (within_limit, message)
        """
        now = timezone.now()
        hourly_start = now - timedelta(hours=1)
        
        # Get hourly message count
        hourly_messages, _ = UsageService.get_user_usage_for_period(
            user, subscription_type, hourly_start, now
        )
        
        # Check against limit
        if subscription_type.hourly_max_messages > 0 and hourly_messages >= subscription_type.hourly_max_messages:
            message = f"شما به حد مجاز پیام‌های ساعتی ({subscription_type.hourly_max_messages} عدد) رسیده‌اید"
            logger.info(f"Hourly message limit exceeded: {message}")
            return False, message
        
        return True, ""
    
    @staticmethod
    def _check_hourly_token_limit(user, subscription_type, ai_model):
        """
        Check hourly token consumption limits
        
        Returns:
            tuple: (within_limit, message)
        """
        now = timezone.now()
        hourly_start = now - timedelta(hours=1)
        
        # Get hourly token count
        _, hourly_tokens = UsageService.get_user_usage_for_period(
            user, subscription_type, hourly_start, now
        )
        
        # Check against limit
        if subscription_type.hourly_max_tokens > 0 and hourly_tokens >= subscription_type.hourly_max_tokens:
            model_type = "رایگان" if ai_model.is_free else "پولی"
            message = f"شما به حد مجاز توکن‌های ساعتی ({subscription_type.hourly_max_tokens} عدد) رسیده‌اید (مدل {model_type})"
            logger.info(f"Hourly token limit exceeded: {message}")
            return False, message
        
        return True, ""
    
    @staticmethod
    def _check_daily_token_limit(user, subscription_type, ai_model):
        """
        Check daily token consumption limits
        
        Returns:
            tuple: (within_limit, message)
        """
        now = timezone.now()
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_end = daily_start + timedelta(days=1)
        
        # Get daily token count
        _, daily_tokens = UsageService.get_user_usage_for_period(
            user, subscription_type, daily_start, daily_end
        )
        
        # Check against limit
        if subscription_type.daily_max_tokens > 0 and daily_tokens >= subscription_type.daily_max_tokens:
            model_type = "رایگان" if ai_model.is_free else "پولی"
            message = f"شما به حد مجاز توکن‌های روزانه ({subscription_type.daily_max_tokens} عدد) رسیده‌اید (مدل {model_type})"
            logger.info(f"Daily token limit exceeded: {message}")
            return False, message
        
        return True, ""
    
    @staticmethod
    def validate_image_reuse_limit(user, session, subscription_type):
        """
        Validation for reusing previously AI-generated images in image chatbots
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if this is an image editing session
        if not (session.chatbot and session.chatbot.chatbot_type == 'image_editing'):
            return True, ""
        
        # For image editing chatbots, we don't need special validation for image reuse
        # as the system automatically uses the last generated image
        return True, ""