from django.utils import timezone
from datetime import timedelta
from .models import UserUsage, SubscriptionType
from chatbot.models import ChatSessionUsage

class UsageService:
    @staticmethod
    def calculate_tokens_for_message(content):
        """
        Calculate tokens for a message (1 token per character)
        """
        return len(content) if content else 0
    
    @staticmethod
    def calculate_tokens_for_messages(messages):
        """
        Calculate total tokens for a list of messages
        """
        total_tokens = 0
        for message in messages:
            total_tokens += UsageService.calculate_tokens_for_message(message.content)
        return total_tokens
    
    @staticmethod
    def check_image_generation_limit(user, subscription_type, is_free_model=False):
        """
        Check if user has exceeded image generation limits based on subscription type configuration
        """
        # Get current time
        now = timezone.now()
        
        # Check daily limit
        if subscription_type.daily_image_generation_limit > 0:
            daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_end = daily_start + timedelta(days=1)
            
            daily_images = UsageService._count_image_generations(user, subscription_type, daily_start, daily_end)
            if daily_images >= subscription_type.daily_image_generation_limit:
                return False, f"شما به حد مجاز تولید تصویر روزانه ({subscription_type.daily_image_generation_limit} عدد) رسیده‌اید"
        
        # Check weekly limit
        if subscription_type.weekly_image_generation_limit > 0:
            weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            weekly_end = weekly_start + timedelta(weeks=1)
            
            weekly_images = UsageService._count_image_generations(user, subscription_type, weekly_start, weekly_end)
            if weekly_images >= subscription_type.weekly_image_generation_limit:
                return False, f"شما به حد مجاز تولید تصویر هفتگی ({subscription_type.weekly_image_generation_limit} عدد) رسیده‌اید"
        
        # Check monthly limit
        if subscription_type.monthly_image_generation_limit > 0:
            monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
            else:
                monthly_end = monthly_start.replace(month=monthly_start.month + 1)
            
            monthly_images = UsageService._count_image_generations(user, subscription_type, monthly_start, monthly_end)
            if monthly_images >= subscription_type.monthly_image_generation_limit:
                return False, f"شما به حد مجاز تولید تصویر ماهانه ({subscription_type.monthly_image_generation_limit} عدد) رسیده‌اید"
        
        # Also check general usage limits
        within_limit, message = UsageService.check_usage_limit(user, subscription_type, 100, is_free_model)
        if not within_limit:
            return False, message
            
        return True, "Usage within limits"
    
    @staticmethod
    def _count_image_generations(user, subscription_type, start_time, end_time):
        """
        Count the number of image generations within a time period
        """
        from chatbot.models import ChatMessage, ChatSession
        
        # Count assistant messages with image URLs in image generation chat sessions
        image_count = ChatMessage.objects.filter(
            session__user=user,
            session__chatbot__chatbot_type='image',
            session__chatbot__subscription_types=subscription_type,
            message_type='assistant',
            image_url__isnull=False,
            image_url__startswith='http',  # Only count actual generated images, not user uploads
            created_at__gte=start_time,
            created_at__lte=end_time
        ).count()
        
        return image_count
    
    @staticmethod
    def check_usage_limit(user, subscription_type, tokens_count=1, is_free_model=False):
        """
        Check if user has exceeded usage limits across ALL time periods
        Also check if total tokens exceed the subscription's max_tokens limit
        """
        # Get current time
        now = timezone.now()
        
        # First check: Total tokens vs Max tokens limit
        if not is_free_model and subscription_type.max_tokens > 0:
            # Calculate total tokens used across all periods
            total_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, subscription_type)[0]
            
            # Check if adding new tokens would exceed the limit
            if total_tokens_used + tokens_count > subscription_type.max_tokens:
                return False, f"تعداد توکن‌های مجاز شما به پایان رسیده است. لطفاً اشتراک خود را ارتقاء دهید."
        
        # Get usage limits from subscription type for ALL time periods
        limits = [
            ('hourly', subscription_type.hourly_max_messages, subscription_type.hourly_max_tokens),
            ('3_hours', subscription_type.three_hours_max_messages, subscription_type.three_hours_max_tokens),
            ('12_hours', subscription_type.twelve_hours_max_messages, subscription_type.twelve_hours_max_tokens),
            ('daily', subscription_type.daily_max_messages, subscription_type.daily_max_tokens),
            ('weekly', subscription_type.weekly_max_messages, subscription_type.weekly_max_tokens),
            ('monthly', subscription_type.monthly_max_messages, subscription_type.monthly_max_tokens),
        ]
        
        # Check each time period
        for time_period, max_messages, max_tokens in limits:
            # Skip if no limit is set for this period
            if max_messages == 0 and max_tokens == 0:
                continue
                
            # Calculate period start and end times
            if time_period == 'hourly':
                period_start = now.replace(minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(hours=1)
            elif time_period == '3_hours':
                # Round down to nearest 3-hour period
                hour_group = (now.hour // 3) * 3
                period_start = now.replace(hour=hour_group, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(hours=3)
            elif time_period == '12_hours':
                # Round down to nearest 12-hour period
                hour_group = (now.hour // 12) * 12
                period_start = now.replace(hour=hour_group, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(hours=12)
            elif time_period == 'daily':
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(days=1)
            elif time_period == 'weekly':
                # Start of week (Monday)
                period_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(weeks=1)
            elif time_period == 'monthly':
                # Start of month
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    period_end = period_start.replace(year=period_start.year + 1, month=1)
                else:
                    period_end = period_start.replace(month=period_start.month + 1)
            
            # Get or create user usage record for this period
            try:
                user_usage = UserUsage.objects.get(
                    user=user,
                    subscription_type=subscription_type,
                    period_start=period_start
                )
            except UserUsage.DoesNotExist:
                # If no record exists, user hasn't used any resources in this period
                continue
            
            # Check limits based on model type
            if is_free_model:
                # For free models, check against monthly free model limits
                if time_period == 'monthly':
                    # Check free model message limit
                    if subscription_type.monthly_free_model_messages > 0 and user_usage.free_model_messages_count >= subscription_type.monthly_free_model_messages:
                        return False, f"تعداد پیام‌های مجاز مدل رایگان در بازه زمانی یک ماه به پایان رسیده است"
                    
                    # Check free model token limit
                    if subscription_type.monthly_free_model_tokens > 0 and user_usage.free_model_tokens_count + tokens_count > subscription_type.monthly_free_model_tokens:
                        return False, f"تعداد توکن‌های مجاز مدل رایگان در بازه زمانی یک ماه به پایان رسیده است"
            else:
                # Check message limit
                if max_messages > 0 and user_usage.messages_count >= max_messages:
                    return False, f"تعداد پیام‌های مجاز در بازه زمانی {time_period} به پایان رسیده است"
                
                # Check token limit
                if max_tokens > 0 and user_usage.tokens_count + tokens_count > max_tokens:
                    return False, f"تعداد توکن‌های مجاز در بازه زمانی {time_period} به پایان رسیده است"
        
        return True, "Usage within limits"
    
    @staticmethod
    def increment_usage(user, subscription_type, messages_count=1, tokens_count=1, is_free_model=False):
        """
        Increment user usage counters - FIXED: Only update one period to avoid duplication
        """
        # Handle case where subscription_type might be None
        if not subscription_type:
            return
        
        # Get current time
        now = timezone.now()
        
        # Get usage limits from subscription type - Only update the most relevant period
        # Order from most granular to least granular
        limits = [
            ('hourly', subscription_type.hourly_max_messages, subscription_type.hourly_max_tokens),
            ('3_hours', subscription_type.three_hours_max_messages, subscription_type.three_hours_max_tokens),
            ('12_hours', subscription_type.twelve_hours_max_messages, subscription_type.twelve_hours_max_tokens),
            ('daily', subscription_type.daily_max_messages, subscription_type.daily_max_tokens),
            ('weekly', subscription_type.weekly_max_messages, subscription_type.weekly_max_tokens),
            ('monthly', subscription_type.monthly_max_messages, subscription_type.monthly_max_tokens),
        ]
        
        # Find the first period that has any limits set (messages or tokens)
        selected_period = None
        for time_period, max_messages, max_tokens in limits:
            if max_messages > 0 or max_tokens > 0:
                selected_period = (time_period, max_messages, max_tokens)
                break
        
        # If no limits are set for any period, use daily as default
        if not selected_period:
            selected_period = ('daily', subscription_type.daily_max_messages, subscription_type.daily_max_tokens)
            
        time_period, max_messages, max_tokens = selected_period
        
        # Calculate period start and end times
        if time_period == 'hourly':
            period_start = now.replace(minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(hours=1)
        elif time_period == '3_hours':
            hour_group = (now.hour // 3) * 3
            period_start = now.replace(hour=hour_group, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(hours=3)
        elif time_period == '12_hours':
            hour_group = (now.hour // 12) * 12
            period_start = now.replace(hour=hour_group, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(hours=12)
        elif time_period == 'daily':
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif time_period == 'weekly':
            period_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(weeks=1)
        elif time_period == 'monthly':
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        
        # Use update_or_create to handle potential race conditions
        user_usage, created = UserUsage.objects.update_or_create(
            user=user,
            subscription_type=subscription_type,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'messages_count': 0,
                'tokens_count': 0,
                'free_model_messages_count': 0,
                'free_model_tokens_count': 0
            }
        )
        
        # Update counters based on model type
        if is_free_model:
            # For free models, update only the monthly free model counters
            if time_period == 'monthly':
                user_usage.free_model_messages_count += messages_count
                user_usage.free_model_tokens_count += tokens_count
                user_usage.save()
            # If free model is used but the selected period is not monthly, 
            # we still need to track it in the monthly period
            elif subscription_type.monthly_free_model_tokens > 0 or subscription_type.monthly_free_model_messages > 0:
                # Get or create the monthly period specifically for free model tracking
                monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
                else:
                    monthly_end = monthly_start.replace(month=monthly_start.month + 1)
                
                monthly_usage, _ = UserUsage.objects.update_or_create(
                    user=user,
                    subscription_type=subscription_type,
                    period_start=monthly_start,
                    defaults={
                        'period_end': monthly_end,
                        'messages_count': 0,
                        'tokens_count': 0,
                        'free_model_messages_count': 0,
                        'free_model_tokens_count': 0
                    }
                )
                monthly_usage.free_model_messages_count += messages_count
                monthly_usage.free_model_tokens_count += tokens_count
                monthly_usage.save()
        else:
            user_usage.messages_count += messages_count
            user_usage.tokens_count += tokens_count
            user_usage.save()
    
    @staticmethod
    def get_user_total_tokens_used(user, subscription_type):
        """
        Calculate the total tokens used by a user for their current subscription period
        This implements the professional subscription logic with proper monthly reset
        """
        from .models import UserSubscription
        
        # Get the user's subscription record
        try:
            user_subscription = UserSubscription.objects.get(user=user, subscription_type=subscription_type, is_active=True)
        except UserSubscription.DoesNotExist:
            # If no active subscription, user might be on a free tier
            # In this case, we'll calculate usage from the beginning of the current month
            now = timezone.now()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            user_usages = UserUsage.objects.filter(
                user=user, 
                subscription_type=subscription_type,
                period_start__gte=period_start
            )
            
            total_tokens = 0
            free_model_tokens = 0
            
            for usage in user_usages:
                total_tokens += usage.tokens_count
                free_model_tokens += usage.free_model_tokens_count
                
            return total_tokens + free_model_tokens
        
        # If user has an active subscription, calculate usage from subscription start date
        subscription_start = user_subscription.start_date
        now = timezone.now()
        
        # For monthly billing cycles, we reset at the beginning of each billing cycle
        # Calculate the start of the current billing period
        if user_subscription.end_date and user_subscription.end_date < now:
            # Subscription has expired, use the end date as reference
            billing_period_start = user_subscription.end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # Subscription is active, use start date to determine billing cycle
            # Calculate how many full billing cycles have passed
            days_since_start = (now - subscription_start).days
            full_cycles = days_since_start // subscription_type.duration_days
            billing_period_start = subscription_start + timedelta(days=full_cycles * subscription_type.duration_days)
            # Reset to beginning of month for cleaner calculation
            billing_period_start = billing_period_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get usage records for the current billing period
        user_usages = UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            period_start__gte=billing_period_start
        )
        
        total_tokens = 0
        free_model_tokens = 0
        
        for usage in user_usages:
            total_tokens += usage.tokens_count
            free_model_tokens += usage.free_model_tokens_count
            
        return total_tokens + free_model_tokens
    
    @staticmethod
    def get_user_free_model_tokens_used(user, subscription_type):
        """
        Calculate the total free model tokens used by a user for the current month
        Free model tokens are always tracked monthly regardless of subscription status
        """
        now = timezone.now()
        # Always calculate from the beginning of the current month for free models
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        user_usages = UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            period_start__gte=period_start
        )
        
        free_model_tokens = 0
        for usage in user_usages:
            free_model_tokens += usage.free_model_tokens_count
            
        return free_model_tokens
    
    @staticmethod
    def reset_user_usage(user, subscription_type):
        """
        Reset user usage counters - typically called when subscription is upgraded, renewed, or expires
        This method now only resets the usage counters but does not delete the data
        """
        # Instead of deleting usage records, we just reset the counters
        # This ensures that data is never deleted from the server as requested
        UserUsage.objects.filter(user=user, subscription_type=subscription_type).update(
            messages_count=0,
            tokens_count=0,
            free_model_messages_count=0,
            free_model_tokens_count=0
        )
    
    @staticmethod
    def get_user_total_tokens_from_chat_sessions(user, subscription_type):
        """
        Calculate the total tokens used by a user based on ChatSessionUsage records
        This implements the new requirement where tokens are tracked per chat session
        """
        # Sum up all tokens from ChatSessionUsage records for this user and subscription type
        chat_session_usages = ChatSessionUsage.objects.filter(
            user=user,
            subscription_type=subscription_type
        )
        
        total_tokens = 0
        free_model_tokens = 0
        
        for usage in chat_session_usages:
            total_tokens += usage.tokens_count
            free_model_tokens += usage.free_model_tokens_count
            
        return total_tokens, free_model_tokens
    
    @staticmethod
    def reset_monthly_free_tokens():
        """
        Automatically reset free tokens monthly for all users
        This should be called by a scheduled task (cron job)
        """
        now = timezone.now()
        # Reset at the beginning of each month
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Reset only the free model counters
        UserUsage.objects.filter(period_start__lt=period_start).update(
            free_model_messages_count=0,
            free_model_tokens_count=0
        )
    
    @staticmethod
    def check_web_search_limit(user, subscription_type):
        """
        Check if user has exceeded web search limits based on subscription type configuration
        """
        # Get current time
        now = timezone.now()
        
        # Check daily limit
        if subscription_type.daily_web_search_limit > 0:
            daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_end = daily_start + timedelta(days=1)
            
            daily_searches = UsageService._count_web_searches(user, subscription_type, daily_start, daily_end)
            if daily_searches >= subscription_type.daily_web_search_limit:
                return False, f"شما به حد مجاز استفاده از Web Search روزانه ({subscription_type.daily_web_search_limit} عدد) رسیده‌اید"
        
        # Check weekly limit
        if subscription_type.weekly_web_search_limit > 0:
            weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            weekly_end = weekly_start + timedelta(weeks=1)
            
            weekly_searches = UsageService._count_web_searches(user, subscription_type, weekly_start, weekly_end)
            if weekly_searches >= subscription_type.weekly_web_search_limit:
                return False, f"شما به حد مجاز استفاده از Web Search هفتگی ({subscription_type.weekly_web_search_limit} عدد) رسیده‌اید"
        
        # Check monthly limit
        if subscription_type.monthly_web_search_limit > 0:
            monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
            else:
                monthly_end = monthly_start.replace(month=monthly_start.month + 1)
            
            monthly_searches = UsageService._count_web_searches(user, subscription_type, monthly_start, monthly_end)
            if monthly_searches >= subscription_type.monthly_web_search_limit:
                return False, f"شما به حد مجاز استفاده از Web Search ماهانه ({subscription_type.monthly_web_search_limit} عدد) رسیده‌اید"
        
        return True, "Usage within limits"
    
    @staticmethod
    def _count_web_searches(user, subscription_type, start_time, end_time):
        """
        Count the number of web searches within a time period
        This is a placeholder implementation - in a real system, you would track web searches separately
        """
        # For now, we'll return 0 as we don't have a specific model to track web searches
        # In a real implementation, you would have a model to track web search usage
        return 0
    
    @staticmethod
    def check_pdf_processing_limit(user, subscription_type, pdf_file_size_mb=0):
        """
        Check if user has exceeded PDF processing limits based on subscription type configuration
        """
        # Check file size limit first
        if subscription_type.max_pdf_file_size > 0 and pdf_file_size_mb > subscription_type.max_pdf_file_size:
            return False, f"حجم فایل PDF ارسالی ({pdf_file_size_mb} MB) بیشتر از حداکثر مجاز ({subscription_type.max_pdf_file_size} MB) است"
        
        # Get current time
        now = timezone.now()
        
        # Check daily limit
        if subscription_type.daily_pdf_processing_limit > 0:
            daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_end = daily_start + timedelta(days=1)
            
            daily_pdfs = UsageService._count_pdf_processings(user, subscription_type, daily_start, daily_end)
            if daily_pdfs >= subscription_type.daily_pdf_processing_limit:
                return False, f"شما به حد مجاز پردازش PDF روزانه ({subscription_type.daily_pdf_processing_limit} عدد) رسیده‌اید"
        
        # Check weekly limit
        if subscription_type.weekly_pdf_processing_limit > 0:
            weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            weekly_end = weekly_start + timedelta(weeks=1)
            
            weekly_pdfs = UsageService._count_pdf_processings(user, subscription_type, weekly_start, weekly_end)
            if weekly_pdfs >= subscription_type.weekly_pdf_processing_limit:
                return False, f"شما به حد مجاز پردازش PDF هفتگی ({subscription_type.weekly_pdf_processing_limit} عدد) رسیده‌اید"
        
        # Check monthly limit
        if subscription_type.monthly_pdf_processing_limit > 0:
            monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
            else:
                monthly_end = monthly_start.replace(month=monthly_start.month + 1)
            
            monthly_pdfs = UsageService._count_pdf_processings(user, subscription_type, monthly_start, monthly_end)
            if monthly_pdfs >= subscription_type.monthly_pdf_processing_limit:
                return False, f"شما به حد مجاز پردازش PDF ماهانه ({subscription_type.monthly_pdf_processing_limit} عدد) رسیده‌اید"
        
        return True, "Usage within limits"
    
    @staticmethod
    def _count_pdf_processings(user, subscription_type, start_time, end_time):
        """
        Count the number of PDF processings within a time period
        This is a placeholder implementation - in a real system, you would track PDF processings separately
        """
        # For now, we'll return 0 as we don't have a specific model to track PDF processings
        # In a real implementation, you would have a model to track PDF processing usage
        return 0
    
    @staticmethod
    def increment_web_search_usage(user, subscription_type):
        """
        Increment web search usage counter
        This is a placeholder implementation - in a real system, you would track web searches separately
        """
        # In a real implementation, you would increment the web search counter in the database
        pass
    
    @staticmethod
    def increment_pdf_processing_usage(user, subscription_type):
        """
        Increment PDF processing usage counter
        This is a placeholder implementation - in a real system, you would track PDF processings separately
        """
        # In a real implementation, you would increment the PDF processing counter in the database
        pass
