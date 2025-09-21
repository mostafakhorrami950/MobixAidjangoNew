import logging
from django.utils import timezone
from datetime import timedelta
from django.apps import apps
from django.db.models import Sum, Count
from .services import UsageService

# Configure logging
logger = logging.getLogger(__name__)

class UserUsageStatsService:
    """
    سرویس جامع برای محاسبه و نمایش آمارهای مصرف کاربر
    Service for calculating and displaying user usage statistics
    """

    @staticmethod
    def get_user_usage_statistics(user):
        """
        دریافت آمارهای کامل مصرف کاربر برای نمایش در داشبورد و صفحات خرید
        Get complete user usage statistics for dashboard and purchase pages
        """
        logger.info(f"Getting comprehensive usage statistics for user {user.id}")
        
        # Get user's subscription type
        subscription_type = user.get_subscription_type()
        if not subscription_type:
            logger.warning(f"No active subscription found for user {user.id}")
            return UserUsageStatsService._get_empty_stats()
        
        now = timezone.now()
        stats = {}
        
        # 1. Token Statistics (Free and Paid)
        stats['tokens'] = UserUsageStatsService._get_token_statistics(user, subscription_type)
        
        # 2. Message Statistics for different time periods
        stats['messages'] = UserUsageStatsService._get_message_statistics(user, subscription_type, now)
        
        # 3. Image Generation Statistics
        stats['images'] = UserUsageStatsService._get_image_statistics(user, subscription_type, now)
        
        # 4. Subscription Info
        stats['subscription'] = {
            'type': subscription_type.name,
            'description': subscription_type.description,
            'price': float(subscription_type.price),
            'duration_days': subscription_type.duration_days,
        }
        
        logger.debug(f"Generated comprehensive stats for user {user.id}")
        return stats
    
    @staticmethod
    def _get_token_statistics(user, subscription_type):
        """محاسبه آمارهای توکن (رایگان و پولی)"""
        logger.debug("Calculating token statistics")
        
        # Get total tokens from chat sessions
        total_paid_tokens, total_free_tokens = UsageService.get_user_total_tokens_from_chat_sessions(
            user, subscription_type
        )
        
        # Add usage from the old UserUsage model for backward compatibility
        try:
            UserUsage = apps.get_model('subscriptions', 'UserUsage')
            user_usage_records = UserUsage.objects.filter(user=user, subscription_type=subscription_type)
            
            for record in user_usage_records:
                total_paid_tokens += record.tokens_count
                total_free_tokens += record.free_model_tokens_count
            
            logger.info(f"User {user.id} combined tokens - Paid: {total_paid_tokens}, Free: {total_free_tokens}")
            
        except Exception as e:
            logger.error(f"Error getting UserUsage records for user {user.id} in stats: {str(e)}")

        # Calculate remaining tokens
        max_paid_tokens = subscription_type.max_tokens
        max_free_tokens = subscription_type.max_tokens_free
        
        remaining_paid_tokens = max(0, max_paid_tokens - total_paid_tokens) if max_paid_tokens > 0 else float('inf')
        remaining_free_tokens = max(0, max_free_tokens - total_free_tokens) if max_free_tokens > 0 else float('inf')
        
        return {
            'paid': {
                'used': total_paid_tokens,
                'limit': max_paid_tokens,
                'remaining': remaining_paid_tokens if remaining_paid_tokens != float('inf') else None,
                'percentage_used': (total_paid_tokens / max_paid_tokens * 100) if max_paid_tokens > 0 else 0
            },
            'free': {
                'used': total_free_tokens,
                'limit': max_free_tokens,
                'remaining': remaining_free_tokens if remaining_free_tokens != float('inf') else None,
                'percentage_used': (total_free_tokens / max_free_tokens * 100) if max_free_tokens > 0 else 0
            }
        }
    
    @staticmethod
    def _get_message_statistics(user, subscription_type, now):
        """محاسبه آمارهای پیام در بازه‌های زمانی مختلف"""
        logger.debug("Calculating message statistics for different time periods")
        
        time_periods = {
            'hourly': {
                'start': now - timedelta(hours=1),
                'end': now,
                'limit': subscription_type.hourly_max_messages
            },
            'three_hours': {
                'start': now - timedelta(hours=3),
                'end': now,
                'limit': subscription_type.three_hours_max_messages
            },
            'twelve_hours': {
                'start': now - timedelta(hours=12),
                'end': now,
                'limit': subscription_type.twelve_hours_max_messages
            },
            'daily': {
                'start': now.replace(hour=0, minute=0, second=0, microsecond=0),
                'end': now.replace(hour=23, minute=59, second=59, microsecond=999999),
                'limit': subscription_type.daily_max_messages
            },
            'weekly': {
                'start': (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
                'end': (now - timedelta(days=now.weekday()) + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999),
                'limit': subscription_type.weekly_max_messages
            },
            'monthly': {
                'start': now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'end': UserUsageStatsService._get_month_end(now),
                'limit': subscription_type.monthly_max_messages
            }
        }
        
        message_stats = {}
        
        for period_name, period_info in time_periods.items():
            messages_count, tokens_count = UsageService.get_user_usage_for_period(
                user, subscription_type, period_info['start'], period_info['end']
            )
            
            limit = period_info['limit']
            remaining = max(0, limit - messages_count) if limit > 0 else float('inf')
            percentage_used = (messages_count / limit * 100) if limit > 0 else 0
            
            message_stats[period_name] = {
                'used': messages_count,
                'tokens': tokens_count,
                'limit': limit,
                'remaining': remaining if remaining != float('inf') else None,
                'percentage_used': percentage_used,
                'period_start': period_info['start'],
                'period_end': period_info['end']
            }
        
        return message_stats
    
    @staticmethod
    def _get_image_statistics(user, subscription_type, now):
        """محاسبه آمارهای تولید تصویر"""
        logger.debug("Calculating image generation statistics")
        
        ImageGenerationUsage = apps.get_model('chatbot', 'ImageGenerationUsage')
        
        try:
            image_usage = ImageGenerationUsage.objects.get(
                user=user,
                subscription_type=subscription_type
            )
        except ImageGenerationUsage.DoesNotExist:
            image_usage = None
        
        # Calculate periods
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get current counts (reset if periods have changed)
        if image_usage:
            daily_count = image_usage.daily_images_count if image_usage.daily_period_start.date() == daily_start.date() else 0
            weekly_count = image_usage.weekly_images_count if image_usage.weekly_period_start.date() == weekly_start.date() else 0
            monthly_count = image_usage.monthly_images_count if image_usage.monthly_period_start.month == monthly_start.month else 0
        else:
            daily_count = weekly_count = monthly_count = 0
        
        # Get limits
        daily_limit = subscription_type.daily_image_generation_limit
        weekly_limit = subscription_type.weekly_image_generation_limit
        monthly_limit = subscription_type.monthly_image_generation_limit
        
        return {
            'daily': {
                'used': daily_count,
                'limit': daily_limit,
                'remaining': max(0, daily_limit - daily_count) if daily_limit > 0 else None,
                'percentage_used': (daily_count / daily_limit * 100) if daily_limit > 0 else 0
            },
            'weekly': {
                'used': weekly_count,
                'limit': weekly_limit,
                'remaining': max(0, weekly_limit - weekly_count) if weekly_limit > 0 else None,
                'percentage_used': (weekly_count / weekly_limit * 100) if weekly_limit > 0 else 0
            },
            'monthly': {
                'used': monthly_count,
                'limit': monthly_limit,
                'remaining': max(0, monthly_limit - monthly_count) if monthly_limit > 0 else None,
                'percentage_used': (monthly_count / monthly_limit * 100) if monthly_limit > 0 else 0
            }
        }
    
    @staticmethod
    def _get_month_end(date):
        """محاسبه پایان ماه"""
        if date.month == 12:
            return date.replace(year=date.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        else:
            return date.replace(month=date.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
    
    @staticmethod
    def _get_empty_stats():
        """آمارهای خالی برای کاربران بدون اشتراک"""
        return {
            'tokens': {
                'paid': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'free': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0}
            },
            'messages': {
                'hourly': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'three_hours': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'twelve_hours': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'daily': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'weekly': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'monthly': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0}
            },
            'images': {
                'daily': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'weekly': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0},
                'monthly': {'used': 0, 'limit': 0, 'remaining': 0, 'percentage_used': 0}
            },
            'subscription': {
                'type': 'بدون اشتراک',
                'description': 'اشتراک فعالی وجود ندارد',
                'price': 0,
                'duration_days': 0
            }
        }

    @staticmethod
    def get_usage_summary_for_dashboard(user):
        """
        خلاصه مصرف برای نمایش در داشبورد
        Usage summary for dashboard display
        """
        stats = UserUsageStatsService.get_user_usage_statistics(user)
        
        return {
            'tokens_summary': {
                'paid_used': stats['tokens']['paid']['used'],
                'paid_limit': stats['tokens']['paid']['limit'],
                'paid_remaining': stats['tokens']['paid']['remaining'],
                'free_used': stats['tokens']['free']['used'],
                'free_limit': stats['tokens']['free']['limit'],
                'free_remaining': stats['tokens']['free']['remaining'],
            },
            'messages_today': {
                'used': stats['messages']['daily']['used'],
                'limit': stats['messages']['daily']['limit'],
                'remaining': stats['messages']['daily']['remaining'],
            },
            'images_today': {
                'used': stats['images']['daily']['used'],
                'limit': stats['images']['daily']['limit'],
                'remaining': stats['images']['daily']['remaining'],
            },
            'subscription_name': stats['subscription']['type']
        }

    @staticmethod
    def get_usage_cards_data(user):
        """
        داده‌های کارت‌های مصرف برای نمایش در UI
        Usage cards data for UI display
        """
        stats = UserUsageStatsService.get_user_usage_statistics(user)
        
        cards = []
        
        # Token Cards
        cards.append({
            'title': 'توکن‌های پولی',
            'icon': 'fas fa-coins',
            'used': stats['tokens']['paid']['used'],
            'limit': stats['tokens']['paid']['limit'],
            'remaining': stats['tokens']['paid']['remaining'],
            'percentage': stats['tokens']['paid']['percentage_used'],
            'color': 'primary',
            'type': 'tokens_paid'
        })
        
        cards.append({
            'title': 'توکن‌های رایگان',
            'icon': 'fas fa-gift',
            'used': stats['tokens']['free']['used'],
            'limit': stats['tokens']['free']['limit'],
            'remaining': stats['tokens']['free']['remaining'],
            'percentage': stats['tokens']['free']['percentage_used'],
            'color': 'success',
            'type': 'tokens_free'
        })
        
        # Message Cards for different periods
        periods = [
            ('hourly', 'پیام‌های ساعتی', 'fas fa-clock'),
            ('three_hours', 'پیام‌های ۳ ساعته', 'fas fa-hourglass-half'),
            ('twelve_hours', 'پیام‌های ۱۲ ساعته', 'fas fa-hourglass'),
            ('daily', 'پیام‌های روزانه', 'fas fa-calendar-day'),
            ('weekly', 'پیام‌های هفتگی', 'fas fa-calendar-week'),
            ('monthly', 'پیام‌های ماهانه', 'fas fa-calendar-alt')
        ]
        
        for period_key, title, icon in periods:
            if period_key in stats['messages'] and stats['messages'][period_key]['limit'] > 0:
                cards.append({
                    'title': title,
                    'icon': icon,
                    'used': stats['messages'][period_key]['used'],
                    'limit': stats['messages'][period_key]['limit'],
                    'remaining': stats['messages'][period_key]['remaining'],
                    'percentage': stats['messages'][period_key]['percentage_used'],
                    'color': 'info',
                    'type': f'messages_{period_key}'
                })
        
        # Image Generation Cards
        image_periods = [
            ('daily', 'تصاویر روزانه', 'fas fa-image'),
            ('weekly', 'تصاویر هفتگی', 'fas fa-images'),
            ('monthly', 'تصاویر ماهانه', 'fas fa-photo-video')
        ]
        
        for period_key, title, icon in image_periods:
            if period_key in stats['images'] and stats['images'][period_key]['limit'] > 0:
                cards.append({
                    'title': title,
                    'icon': icon,
                    'used': stats['images'][period_key]['used'],
                    'limit': stats['images'][period_key]['limit'],
                    'remaining': stats['images'][period_key]['remaining'],
                    'percentage': stats['images'][period_key]['percentage_used'],
                    'color': 'warning',
                    'type': f'images_{period_key}'
                })
        
        return cards