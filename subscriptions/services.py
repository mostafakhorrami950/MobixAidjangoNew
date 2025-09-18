import logging
from django.utils import timezone
from datetime import timedelta
from django.apps import apps
from django.db.models import Sum
import tiktoken

# Configure logging
logger = logging.getLogger(__name__)

class UsageService:
    @staticmethod
    def calculate_tokens_for_message(content):
        """
        Calculate tokens for a message using tiktoken with cl100k_base encoding (GPT-4/GPT-3.5)
        """
        if not content:
            return 0
        
        try:
            # Use cl100k_base encoding which is used by GPT-4 and GPT-3.5-turbo
            encoding = tiktoken.get_encoding("cl100k_base")
            token_count = len(encoding.encode(str(content)))
            logger.debug(f"Calculated tokens for message using tiktoken: {token_count}")
            return token_count
        except Exception as e:
            logger.error(f"Error calculating tokens with tiktoken: {str(e)}")
            # Fallback to character-based estimation (roughly 4 characters per token)
            token_count = max(1, len(str(content)) // 4)
            logger.debug(f"Used fallback token calculation: {token_count}")
            return token_count
    
    @staticmethod
    def calculate_tokens_for_messages(messages):
        """
        Calculate total tokens for a list of messages
        """
        total_tokens = 0
        for message in messages:
            total_tokens += UsageService.calculate_tokens_for_message(message.content)
        logger.debug(f"Calculated total tokens for messages: {total_tokens}")
        return total_tokens
    
    @staticmethod
    def check_usage_limit(user, subscription_type, tokens_count=1, is_free_model=False):
        """
        Check if user has exceeded usage limits across ALL time periods
        Also check if total tokens exceed the subscription's max_tokens limit
        """
        logger.info(f"Checking usage limits for user {user.id}, is_free_model: {is_free_model}")
        
        # Get current time
        now = timezone.now()
        logger.debug(f"Current time: {now}")
        
        # First check: Total tokens vs Max tokens limit
        if not is_free_model and subscription_type.max_tokens > 0:
            # Calculate total tokens used across all periods
            total_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, subscription_type)[0]
            logger.debug(f"Total tokens used: {total_tokens_used}, Max tokens: {subscription_type.max_tokens}")
            
            # Check if adding new tokens would exceed the limit
            if total_tokens_used + tokens_count > subscription_type.max_tokens:
                message = f"شما به حد مجاز توکن‌های مصرفی ({subscription_type.max_tokens} عدد) رسیده‌اید"
                logger.info(f"Usage limit exceeded: {message}")
                return False, message
        
        # Check hourly limits
        if subscription_type.hourly_max_messages > 0 or subscription_type.hourly_max_tokens > 0:
            hourly_start = now - timedelta(hours=1)
            hourly_messages, hourly_tokens = UsageService.get_user_usage_for_period(
                user, subscription_type, hourly_start, now
            )
            logger.debug(f"Hourly usage - Messages: {hourly_messages}, Tokens: {hourly_tokens}")
            logger.debug(f"Hourly limits - Messages: {subscription_type.hourly_max_messages}, Tokens: {subscription_type.hourly_max_tokens}")
            
            if subscription_type.hourly_max_messages > 0 and hourly_messages >= subscription_type.hourly_max_messages:
                message = f"شما به حد مجاز پیام‌های ساعتی ({subscription_type.hourly_max_messages} عدد) رسیده‌اید"
                logger.info(f"Hourly message limit exceeded: {message}")
                return False, message
            
            if subscription_type.hourly_max_tokens > 0 and hourly_tokens >= subscription_type.hourly_max_tokens:
                message = f"شما به حد مجاز توکن‌های ساعتی ({subscription_type.hourly_max_tokens} عدد) رسیده‌اید"
                logger.info(f"Hourly token limit exceeded: {message}")
                return False, message
        
        # Check 3-hour limits
        if subscription_type.three_hours_max_messages > 0 or subscription_type.three_hours_max_tokens > 0:
            three_hours_start = now - timedelta(hours=3)
            three_hours_messages, three_hours_tokens = UsageService.get_user_usage_for_period(
                user, subscription_type, three_hours_start, now
            )
            logger.debug(f"3-hour usage - Messages: {three_hours_messages}, Tokens: {three_hours_tokens}")
            logger.debug(f"3-hour limits - Messages: {subscription_type.three_hours_max_messages}, Tokens: {subscription_type.three_hours_max_tokens}")
            
            if subscription_type.three_hours_max_messages > 0 and three_hours_messages >= subscription_type.three_hours_max_messages:
                message = f"شما به حد مجاز پیام‌های ۳ ساعتی ({subscription_type.three_hours_max_messages} عدد) رسیده‌اید"
                logger.info(f"3-hour message limit exceeded: {message}")
                return False, message
            
            if subscription_type.three_hours_max_tokens > 0 and three_hours_tokens >= subscription_type.three_hours_max_tokens:
                message = f"شما به حد مجاز توکن‌های ۳ ساعتی ({subscription_type.three_hours_max_tokens} عدد) رسیده‌اید"
                logger.info(f"3-hour token limit exceeded: {message}")
                return False, message
        
        # Check 12-hour limits
        if subscription_type.twelve_hours_max_messages > 0 or subscription_type.twelve_hours_max_tokens > 0:
            twelve_hours_start = now - timedelta(hours=12)
            twelve_hours_messages, twelve_hours_tokens = UsageService.get_user_usage_for_period(
                user, subscription_type, twelve_hours_start, now
            )
            logger.debug(f"12-hour usage - Messages: {twelve_hours_messages}, Tokens: {twelve_hours_tokens}")
            logger.debug(f"12-hour limits - Messages: {subscription_type.twelve_hours_max_messages}, Tokens: {subscription_type.twelve_hours_max_tokens}")
            
            if subscription_type.twelve_hours_max_messages > 0 and twelve_hours_messages >= subscription_type.twelve_hours_max_messages:
                message = f"شما به حد مجاز پیام‌های ۱۲ ساعتی ({subscription_type.twelve_hours_max_messages} عدد) رسیده‌اید"
                logger.info(f"12-hour message limit exceeded: {message}")
                return False, message
            
            if subscription_type.twelve_hours_max_tokens > 0 and twelve_hours_tokens >= subscription_type.twelve_hours_max_tokens:
                message = f"شما به حد مجاز توکن‌های ۱۲ ساعتی ({subscription_type.twelve_hours_max_tokens} عدد) رسیده‌اید"
                logger.info(f"12-hour token limit exceeded: {message}")
                return False, message
        
        # Check daily limits
        if subscription_type.daily_max_messages > 0 or subscription_type.daily_max_tokens > 0:
            daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_end = daily_start + timedelta(days=1)
            
            daily_messages, daily_tokens = UsageService.get_user_usage_for_period(
                user, subscription_type, daily_start, daily_end
            )
            logger.debug(f"Daily usage - Messages: {daily_messages}, Tokens: {daily_tokens}")
            logger.debug(f"Daily limits - Messages: {subscription_type.daily_max_messages}, Tokens: {subscription_type.daily_max_tokens}")
            
            if subscription_type.daily_max_messages > 0 and daily_messages >= subscription_type.daily_max_messages:
                message = f"شما به حد مجاز پیام‌های روزانه ({subscription_type.daily_max_messages} عدد) رسیده‌اید"
                logger.info(f"Daily message limit exceeded: {message}")
                return False, message
            
            if subscription_type.daily_max_tokens > 0 and daily_tokens >= subscription_type.daily_max_tokens:
                message = f"شما به حد مجاز توکن‌های روزانه ({subscription_type.daily_max_tokens} عدد) رسیده‌اید"
                logger.info(f"Daily token limit exceeded: {message}")
                return False, message
        
        # Check weekly limits
        if subscription_type.weekly_max_messages > 0 or subscription_type.weekly_max_tokens > 0:
            weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            weekly_end = weekly_start + timedelta(weeks=1)
            
            weekly_messages, weekly_tokens = UsageService.get_user_usage_for_period(
                user, subscription_type, weekly_start, weekly_end
            )
            logger.debug(f"Weekly usage - Messages: {weekly_messages}, Tokens: {weekly_tokens}")
            logger.debug(f"Weekly limits - Messages: {subscription_type.weekly_max_messages}, Tokens: {subscription_type.weekly_max_tokens}")
            
            if subscription_type.weekly_max_messages > 0 and weekly_messages >= subscription_type.weekly_max_messages:
                message = f"شما به حد مجاز پیام‌های هفتگی ({subscription_type.weekly_max_messages} عدد) رسیده‌اید"
                logger.info(f"Weekly message limit exceeded: {message}")
                return False, message
            
            if subscription_type.weekly_max_tokens > 0 and weekly_tokens >= subscription_type.weekly_max_tokens:
                message = f"شما به حد مجاز توکن‌های هفتگی ({subscription_type.weekly_max_tokens} عدد) رسیده‌اید"
                logger.info(f"Weekly token limit exceeded: {message}")
                return False, message
        
        # Check monthly limits
        if subscription_type.monthly_max_messages > 0 or subscription_type.monthly_max_tokens > 0:
            monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
            else:
                monthly_end = monthly_start.replace(month=monthly_start.month + 1)
            
            monthly_messages, monthly_tokens = UsageService.get_user_usage_for_period(
                user, subscription_type, monthly_start, monthly_end
            )
            logger.debug(f"Monthly usage - Messages: {monthly_messages}, Tokens: {monthly_tokens}")
            logger.debug(f"Monthly limits - Messages: {subscription_type.monthly_max_messages}, Tokens: {subscription_type.monthly_max_tokens}")
            
            if subscription_type.monthly_max_messages > 0 and monthly_messages >= subscription_type.monthly_max_messages:
                message = f"شما به حد مجاز پیام‌های ماهانه ({subscription_type.monthly_max_messages} عدد) رسیده‌اید"
                logger.info(f"Monthly message limit exceeded: {message}")
                return False, message
            
            if subscription_type.monthly_max_tokens > 0 and monthly_tokens >= subscription_type.monthly_max_tokens:
                message = f"شما به حد مجاز توکن‌های ماهانه ({subscription_type.monthly_max_tokens} عدد) رسیده‌اید"
                logger.info(f"Monthly token limit exceeded: {message}")
                return False, message
        
        # Check free model limits (monthly)
        if is_free_model and (subscription_type.monthly_free_model_messages > 0 or subscription_type.monthly_free_model_tokens > 0):
            monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
            else:
                monthly_end = monthly_start.replace(month=monthly_start.month + 1)
            
            monthly_messages, monthly_tokens = UsageService.get_user_free_model_usage_for_period(
                user, subscription_type, monthly_start, monthly_end
            )
            logger.debug(f"Monthly free model usage - Messages: {monthly_messages}, Tokens: {monthly_tokens}")
            logger.debug(f"Monthly free model limits - Messages: {subscription_type.monthly_free_model_messages}, Tokens: {subscription_type.monthly_free_model_tokens}")
            
            if subscription_type.monthly_free_model_messages > 0 and monthly_messages >= subscription_type.monthly_free_model_messages:
                message = f"شما به حد مجاز پیام‌های مدل رایگان ماهانه ({subscription_type.monthly_free_model_messages} عدد) رسیده‌اید"
                logger.info(f"Monthly free model message limit exceeded: {message}")
                return False, message
            
            if subscription_type.monthly_free_model_tokens > 0 and monthly_tokens >= subscription_type.monthly_free_model_tokens:
                message = f"شما به حد مجاز توکن‌های مدل رایگان ماهانه ({subscription_type.monthly_free_model_tokens} عدد) رسیده‌اید"
                logger.info(f"Monthly free model token limit exceeded: {message}")
                return False, message
        
        logger.info("All usage limits are within acceptable range")
        return True, ""
    
    @staticmethod
    def get_user_usage_for_period(user, subscription_type, start_time, end_time):
        """
        Get user's message and token usage for a specific period
        Returns (messages_count, tokens_count)
        """
        logger.debug(f"Getting user usage for period: {start_time} to {end_time}")
        
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        
        usage_data = UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            created_at__gte=start_time,
            created_at__lte=end_time
        ).aggregate(
            total_messages=Sum('messages_count'),
            total_tokens=Sum('tokens_count'),
            total_free_tokens=Sum('free_model_tokens_count')
        )
        
        total_messages = usage_data['total_messages'] or 0
        total_tokens = (usage_data['total_tokens'] or 0) + (usage_data['total_free_tokens'] or 0)
        
        logger.debug(f"Period usage data - Messages: {total_messages}, Tokens: {total_tokens}")
        return total_messages, total_tokens
    
    @staticmethod
    def get_user_free_model_usage_for_period(user, subscription_type, start_time, end_time):
        """
        Get user's free model usage for a specific period
        Returns (messages_count, tokens_count)
        """
        logger.debug(f"Getting user free model usage for period: {start_time} to {end_time}")
        
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        
        usage_data = UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            created_at__gte=start_time,
            created_at__lte=end_time
        ).aggregate(
            total_messages=Sum('free_model_messages_count'),
            total_tokens=Sum('free_model_tokens_count')
        )
        
        total_messages = usage_data['total_messages'] or 0
        total_tokens = usage_data['total_tokens'] or 0
        
        logger.debug(f"Free model period usage data - Messages: {total_messages}, Tokens: {total_tokens}")
        return total_messages, total_tokens
    
    @staticmethod
    def get_user_total_tokens_from_chat_sessions(user, subscription_type):
        """
        Get total tokens used by user across all chat sessions for a subscription type
        Returns (total_tokens, free_model_tokens)
        """
        logger.debug(f"Getting total tokens from chat sessions for user {user.id}")
        
        ChatSessionUsage = apps.get_model('chatbot', 'ChatSessionUsage')
        chat_session_usages = ChatSessionUsage.objects.filter(
            user=user,
            subscription_type=subscription_type
        )
        
        total_tokens = 0
        free_model_tokens = 0
        for usage in chat_session_usages:
            total_tokens += usage.tokens_count
            free_model_tokens += usage.free_model_tokens_count
        
        logger.debug(f"Total tokens from chat sessions - Total: {total_tokens}, Free model: {free_model_tokens}")
        return total_tokens, free_model_tokens
    
    @staticmethod
    def increment_usage(user, subscription_type, messages_count=1, tokens_count=1, is_free_model=False):
        """
        Create a new usage record for each event.
        """
        logger.info(f"Incrementing usage for user {user.id}, is_free_model: {is_free_model}")
        logger.debug(f"Messages count: {messages_count}, Tokens count: {tokens_count}")
        
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        
        defaults = {
            'messages_count': 0,
            'tokens_count': 0,
            'free_model_messages_count': 0,
            'free_model_tokens_count': 0
        }
        
        if is_free_model:
            defaults['free_model_messages_count'] = messages_count
            defaults['free_model_tokens_count'] = tokens_count
        else:
            defaults['messages_count'] = messages_count
            defaults['tokens_count'] = tokens_count
            
        usage_record = UserUsage.objects.create(
            user=user,
            subscription_type=subscription_type,
            **defaults
        )
        
        logger.debug(f"Created usage record with ID: {usage_record.id}")
        return usage_record

    @staticmethod
    def reset_user_usage(user, subscription_type):
        """
        Reset user's usage counters for a subscription type without deleting data
        This method sets all counters to zero while preserving the usage records
        """
        logger.info(f"Resetting user usage for user {user.id}")
        
        # Get all usage records for this user and subscription type
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        usage_records = UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type
        )
        
        # Reset all counters to zero
        for record in usage_records:
            record.messages_count = 0
            record.tokens_count = 0
            record.free_model_messages_count = 0
            record.free_model_tokens_count = 0
            record.save()
            logger.debug(f"Reset usage record ID: {record.id}")

    @staticmethod
    def check_image_generation_limit(user, subscription_type):
        """
        Check if user has exceeded image generation limits
        Returns (within_limit, message)
        """
        logger.info(f"Checking image generation limits for user {user.id}")
        
        now = timezone.now()
        
        # Get or create image generation usage record
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        ImageGenerationUsage = apps.get_model('chatbot', 'ImageGenerationUsage')
        image_usage, created = ImageGenerationUsage.objects.get_or_create(
            user=user,
            subscription_type=subscription_type,
            defaults={
                'daily_images_count': 0,
                'weekly_images_count': 0,
                'monthly_images_count': 0,
                'daily_period_start': daily_start,
                'weekly_period_start': weekly_start,
                'monthly_period_start': monthly_start,
            }
        )
        
        # Check daily limit
        if subscription_type.daily_image_generation_limit > 0:
            # Reset counter if period has changed
            if image_usage.daily_period_start.date() != daily_start.date():
                image_usage.daily_images_count = 0
                image_usage.daily_period_start = daily_start
            
            if image_usage.daily_images_count >= subscription_type.daily_image_generation_limit:
                message = f"شما به حد مجاز تولید تصویر روزانه ({subscription_type.daily_image_generation_limit} عدد) رسیده‌اید"
                logger.info(f"Daily image generation limit exceeded: {message}")
                return False, message
        
        # Check weekly limit
        if subscription_type.weekly_image_generation_limit > 0:
            # Reset counter if period has changed
            if image_usage.weekly_period_start.date() != weekly_start.date():
                image_usage.weekly_images_count = 0
                image_usage.weekly_period_start = weekly_start
            
            if image_usage.weekly_images_count >= subscription_type.weekly_image_generation_limit:
                message = f"شما به حد مجاز تولید تصویر هفتگی ({subscription_type.weekly_image_generation_limit} عدد) رسیده‌اید"
                logger.info(f"Weekly image generation limit exceeded: {message}")
                return False, message
        
        # Check monthly limit
        if subscription_type.monthly_image_generation_limit > 0:
            # Reset counter if period has changed
            if image_usage.monthly_period_start.month != monthly_start.month:
                image_usage.monthly_images_count = 0
                image_usage.monthly_period_start = monthly_start
            
            if image_usage.monthly_images_count >= subscription_type.monthly_image_generation_limit:
                message = f"شما به حد مجاز تولید تصویر ماهانه ({subscription_type.monthly_image_generation_limit} عدد) رسیده‌اید"
                logger.info(f"Monthly image generation limit exceeded: {message}")
                return False, message
        
        logger.info("Image generation limits are within acceptable range")
        return True, ""

    @staticmethod
    def increment_image_generation_usage(user, subscription_type):
        """
        Increment user's image generation usage counters
        """
        logger.info(f"Incrementing image generation usage for user {user.id}")
        
        now = timezone.now()
        
        # Get or create image generation usage record
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        ImageGenerationUsage = apps.get_model('chatbot', 'ImageGenerationUsage')
        image_usage, created = ImageGenerationUsage.objects.get_or_create(
            user=user,
            subscription_type=subscription_type,
            defaults={
                'daily_images_count': 0,
                'weekly_images_count': 0,
                'monthly_images_count': 0,
                'daily_period_start': daily_start,
                'weekly_period_start': weekly_start,
                'monthly_period_start': monthly_start,
            }
        )
        
        # Increment all counters
        image_usage.daily_images_count += 1
        image_usage.weekly_images_count += 1
        image_usage.monthly_images_count += 1
        
        # Update period start times if needed
        if image_usage.daily_period_start.date() != daily_start.date():
            image_usage.daily_period_start = daily_start
        
        if image_usage.weekly_period_start.date() != weekly_start.date():
            image_usage.weekly_period_start = weekly_start
        
        if image_usage.monthly_period_start.month != monthly_start.month:
            image_usage.monthly_period_start = monthly_start
        
        image_usage.save()
        logger.debug("Image generation usage incremented successfully")

    @staticmethod
    def comprehensive_check(user, ai_model, subscription_type):
        """
        Comprehensive check before sending any message to AI
        This method checks all requirements before allowing AI interaction
        """
        logger.info(f"Starting comprehensive check for user {user.id}, AI model: {ai_model.name}, Subscription: {subscription_type.name}")
        
        # 1. Check if user has access to the selected model
        if not user.has_access_to_model(ai_model):
            message = "دسترسی به این مدل دیگر برای اشتراک شما فعال نیست"
            logger.info(f"Model access denied: {message}")
            return False, message
        
        # 2. Check if it's a free model and if free model limits are exceeded
        is_free_model = ai_model.is_free
        logger.debug(f"Is free model: {is_free_model}")
        
        if is_free_model:
            logger.info("Processing free model usage checks")
            
            # Check free model token limits using the new max_tokens_free field
            if subscription_type.max_tokens_free > 0:
                logger.debug(f"Checking max_tokens_free limit: {subscription_type.max_tokens_free}")
                
                # Get total free tokens used
                total_free_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, subscription_type)[1]
                logger.debug(f"Total free tokens used: {total_free_tokens_used}")
                
                # Check if adding new tokens would exceed the max_tokens_free limit
                if total_free_tokens_used >= subscription_type.max_tokens_free:
                    message = f"شما به حد مجاز توکن‌های رایگان ({subscription_type.max_tokens_free} عدد) رسیده‌اید"
                    logger.info(f"Max free tokens limit exceeded: {message}")
                    return False, message
            
            # Check all time-based usage limits for free models (independent of max_tokens_free)
            # Get current time
            now = timezone.now()
            logger.debug(f"Current time for time-based checks: {now}")
            
            # Hourly limits for free models
            if subscription_type.hourly_max_tokens > 0:
                logger.debug(f"Checking hourly limit: {subscription_type.hourly_max_tokens}")
                hourly_start = now - timedelta(hours=1)
                hourly_messages, hourly_tokens = UsageService.get_user_free_model_usage_for_period(
                    user, subscription_type, hourly_start, now
                )
                logger.debug(f"Hourly free model usage - Messages: {hourly_messages}, Tokens: {hourly_tokens}")
                
                if hourly_tokens >= subscription_type.hourly_max_tokens:
                    message = f"شما به حد مجاز توکن‌های ساعتی ({subscription_type.hourly_max_tokens} عدد) رسیده‌اید"
                    logger.info(f"Hourly free model token limit exceeded: {message}")
                    return False, message
            
            # 3-hour limits for free models
            if subscription_type.three_hours_max_tokens > 0:
                logger.debug(f"Checking 3-hour limit: {subscription_type.three_hours_max_tokens}")
                three_hours_start = now - timedelta(hours=3)
                three_hours_messages, three_hours_tokens = UsageService.get_user_free_model_usage_for_period(
                    user, subscription_type, three_hours_start, now
                )
                logger.debug(f"3-hour free model usage - Messages: {three_hours_messages}, Tokens: {three_hours_tokens}")
                
                if three_hours_tokens >= subscription_type.three_hours_max_tokens:
                    message = f"شما به حد مجاز توکن‌های ۳ ساعتی ({subscription_type.three_hours_max_tokens} عدد) رسیده‌اید"
                    logger.info(f"3-hour free model token limit exceeded: {message}")
                    return False, message
            
            # 12-hour limits for free models
            if subscription_type.twelve_hours_max_tokens > 0:
                logger.debug(f"Checking 12-hour limit: {subscription_type.twelve_hours_max_tokens}")
                twelve_hours_start = now - timedelta(hours=12)
                twelve_hours_messages, twelve_hours_tokens = UsageService.get_user_free_model_usage_for_period(
                    user, subscription_type, twelve_hours_start, now
                )
                logger.debug(f"12-hour free model usage - Messages: {twelve_hours_messages}, Tokens: {twelve_hours_tokens}")
                
                if twelve_hours_tokens >= subscription_type.twelve_hours_max_tokens:
                    message = f"شما به حد مجاز توکن‌های ۱۲ ساعتی ({subscription_type.twelve_hours_max_tokens} عدد) رسیده‌اید"
                    logger.info(f"12-hour free model token limit exceeded: {message}")
                    return False, message
            
            # Daily limits for free models
            if subscription_type.daily_max_tokens > 0:
                logger.debug(f"Checking daily limit: {subscription_type.daily_max_tokens}")
                daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                daily_end = daily_start + timedelta(days=1)
                
                daily_messages, daily_tokens = UsageService.get_user_free_model_usage_for_period(
                    user, subscription_type, daily_start, daily_end
                )
                logger.debug(f"Daily free model usage - Messages: {daily_messages}, Tokens: {daily_tokens}")
                
                if daily_tokens >= subscription_type.daily_max_tokens:
                    message = f"شما به حد مجاز توکن‌های روزانه ({subscription_type.daily_max_tokens} عدد) رسیده‌اید"
                    logger.info(f"Daily free model token limit exceeded: {message}")
                    return False, message
            
            # Weekly limits for free models
            if subscription_type.weekly_max_tokens > 0:
                logger.debug(f"Checking weekly limit: {subscription_type.weekly_max_tokens}")
                weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
                weekly_end = weekly_start + timedelta(weeks=1)
                
                weekly_messages, weekly_tokens = UsageService.get_user_free_model_usage_for_period(
                    user, subscription_type, weekly_start, weekly_end
                )
                logger.debug(f"Weekly free model usage - Messages: {weekly_messages}, Tokens: {weekly_tokens}")
                
                if weekly_tokens >= subscription_type.weekly_max_tokens:
                    message = f"شما به حد مجاز توکن‌های هفتگی ({subscription_type.weekly_max_tokens} عدد) رسیده‌اید"
                    logger.info(f"Weekly free model token limit exceeded: {message}")
                    return False, message
            
            # Monthly limits for free models
            if subscription_type.monthly_max_tokens > 0:
                logger.debug(f"Checking monthly limit: {subscription_type.monthly_max_tokens}")
                monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
                else:
                    monthly_end = monthly_start.replace(month=monthly_start.month + 1)
                
                monthly_messages, monthly_tokens = UsageService.get_user_free_model_usage_for_period(
                    user, subscription_type, monthly_start, monthly_end
                )
                logger.debug(f"Monthly free model usage - Messages: {monthly_messages}, Tokens: {monthly_tokens}")
                
                if monthly_tokens >= subscription_type.monthly_max_tokens:
                    message = f"شما به حد مجاز توکن‌های ماهانه ({subscription_type.monthly_max_tokens} عدد) رسیده‌اید"
                    logger.info(f"Monthly free model token limit exceeded: {message}")
                    return False, message
            
            # Check free model message limits
            if subscription_type.monthly_free_model_messages > 0 or subscription_type.monthly_free_model_tokens > 0:
                logger.debug(f"Checking monthly free model message limits - Messages: {subscription_type.monthly_free_model_messages}, Tokens: {subscription_type.monthly_free_model_tokens}")
                monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
                else:
                    monthly_end = monthly_start.replace(month=monthly_start.month + 1)
                
                monthly_messages, monthly_tokens = UsageService.get_user_free_model_usage_for_period(
                    user, subscription_type, monthly_start, monthly_end
                )
                logger.debug(f"Monthly free model usage for message limits - Messages: {monthly_messages}, Tokens: {monthly_tokens}")
                
                if subscription_type.monthly_free_model_messages > 0 and monthly_messages >= subscription_type.monthly_free_model_messages:
                    message = f"شما به حد مجاز پیام‌های مدل رایگان ماهانه ({subscription_type.monthly_free_model_messages} عدد) رسیده‌اید"
                    logger.info(f"Monthly free model message limit exceeded: {message}")
                    return False, message
                
                if subscription_type.monthly_free_model_tokens > 0 and monthly_tokens >= subscription_type.monthly_free_model_tokens:
                    message = f"شما به حد مجاز توکن‌های مدل رایگان ماهانه ({subscription_type.monthly_free_model_tokens} عدد) رسیده‌اید"
                    logger.info(f"Monthly free model token limit exceeded: {message}")
                    return False, message
        
        # 3. Check all time-based usage limits for non-free models
        # We'll estimate a reasonable token count for the message
        estimated_tokens = 100  # Default estimation
        logger.debug(f"Estimated tokens for non-free model check: {estimated_tokens}")
        
        within_limit, message = UsageService.check_usage_limit(
            user, subscription_type, estimated_tokens, is_free_model
        )
        if not within_limit:
            logger.info(f"Non-free model usage limit exceeded: {message}")
            return False, message
        
        # 4. If this is a premium model, check max_token limit for the subscription
        if not is_free_model and subscription_type.max_tokens > 0:
            logger.debug(f"Checking max_tokens limit for premium model: {subscription_type.max_tokens}")
            total_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, subscription_type)[0]
            remaining_tokens = subscription_type.max_tokens - total_tokens_used
            logger.debug(f"Total tokens used: {total_tokens_used}, Remaining tokens: {remaining_tokens}")
            
            # If remaining tokens are less than a reasonable threshold, deny access
            if remaining_tokens < estimated_tokens:
                message = f"بودجه باقیمانده‌ی توکن شما برای این مدل کافی نیست ({remaining_tokens} عدد)"
                logger.info(f"Insufficient token budget: {message}")
                return False, message
        
        logger.info("Comprehensive check passed - all limits are within acceptable range")
        return True, ""

    @staticmethod
    def reset_chat_session_usage(user, subscription_type):
        """
        Reset user's chat session usage for a subscription type.
        This method deletes all ChatSessionUsage records for the user and subscription type
        to ensure tokens are properly reset after payment or subscription changes.
        """
        logger.info(f"Resetting chat session usage for user {user.id}, subscription {subscription_type.name}")
        
        try:
            ChatSessionUsage = apps.get_model('chatbot', 'ChatSessionUsage')
            deleted_count, _ = ChatSessionUsage.objects.filter(
                user=user,
                subscription_type=subscription_type
            ).delete()
            
            logger.debug(f"Deleted {deleted_count} chat session usage records for user {user.id}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error resetting chat session usage for user {user.id}: {str(e)}")
            return 0
