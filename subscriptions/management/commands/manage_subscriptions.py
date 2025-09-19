from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from subscriptions.subscription_manager import SubscriptionManager
from subscriptions.models import DefaultSubscriptionSettings, SubscriptionType, UserSubscription
from accounts.models import User
import logging

class Command(BaseCommand):
    help = 'مدیریت اشتراک‌ها و تنظیمات پیش‌فرض'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=[
                'check_expired', 
                'assign_defaults', 
                'stats', 
                'validate', 
                'setup_defaults',
                'fix_users_without_subscription'
            ],
            required=True,
            help='عمل مورد نظر'
        )
        
        parser.add_argument(
            '--plan-name',
            type=str,
            help='نام پلن برای تنظیم پیش‌فرض (برای setup_defaults)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='اجرای تست بدون اعمال تغییرات'
        )

    def handle(self, *args, **options):
        action = options['action']
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔄 حالت تست - تغییرات اعمال نمی‌شوند'))
        
        try:
            if action == 'check_expired':
                self.handle_expired_subscriptions(dry_run)
            elif action == 'assign_defaults':
                self.assign_default_subscriptions(dry_run)
            elif action == 'stats':
                self.show_statistics()
            elif action == 'validate':
                self.validate_settings()
            elif action == 'setup_defaults':
                self.setup_default_settings(options.get('plan_name'), dry_run)
            elif action == 'fix_users_without_subscription':
                self.fix_users_without_subscription(dry_run)
        except Exception as e:
            raise CommandError(f'خطا در اجرای دستور: {str(e)}')

    def handle_expired_subscriptions(self, dry_run=False):
        """مدیریت اشتراک‌های منقضی شده"""
        self.stdout.write(self.style.SUCCESS('🕐 شروع بررسی اشتراک‌های منقضی شده...'))
        
        if dry_run:
            # فقط شمارش
            expired_count = UserSubscription.objects.filter(
                is_active=True,
                end_date__lte=timezone.now()
            ).count()
            self.stdout.write(f'📊 تعداد اشتراک‌های منقضی شده: {expired_count}')
        else:
            total_checked, processed = SubscriptionManager.check_and_handle_expired_subscriptions()
            self.stdout.write(self.style.SUCCESS(
                f'✅ پایان پردازش: {processed}/{total_checked} اشتراک منقضی پردازش شد'
            ))

    def assign_default_subscriptions(self, dry_run=False):
        """تخصیص پلن پیش‌فرض به کاربران بدون اشتراک"""
        self.stdout.write(self.style.SUCCESS('👥 شروع تخصیص پلن پیش‌فرض...'))
        
        users_without_subscription = SubscriptionManager.get_users_without_subscription()
        total_users = len(users_without_subscription)
        
        if dry_run:
            self.stdout.write(f'📊 تعداد کاربران بدون اشتراک: {total_users}')
            # نمایش چند کاربر اول
            if total_users > 0:
                self.stdout.write('📋 نمونه کاربران:')
                for user in users_without_subscription[:5]:
                    self.stdout.write(f'  - {user.name} ({user.phone_number})')
                if total_users > 5:
                    self.stdout.write(f'  ... و {total_users - 5} کاربر دیگر')
        else:
            total, success = SubscriptionManager.assign_default_to_users_without_subscription()
            self.stdout.write(self.style.SUCCESS(
                f'✅ پایان تخصیص: {success}/{total} تخصیص موفق'
            ))

    def show_statistics(self):
        """نمایش آمار اشتراک‌ها"""
        self.stdout.write(self.style.SUCCESS('📊 آمار اشتراک‌ها:'))
        
        stats = SubscriptionManager.get_subscription_statistics()
        
        if stats:
            self.stdout.write(f'👥 کل کاربران: {stats["total_users"]}')
            self.stdout.write(f'✅ کاربران با اشتراک: {stats["users_with_subscription"]}')
            self.stdout.write(f'❌ کاربران بدون اشتراک: {stats["users_without_subscription"]}')
            self.stdout.write(f'🟢 اشتراک‌های فعال: {stats["active_subscriptions"]}')
            self.stdout.write(f'🔴 اشتراک‌های منقضی: {stats["expired_subscriptions"]}')
            
            self.stdout.write('\n📈 آمار بر اساس نوع اشتراک:')
            for plan_name, count in stats['subscription_types'].items():
                self.stdout.write(f'  {plan_name}: {count} کاربر')
        else:
            self.stdout.write(self.style.ERROR('❌ خطا در دریافت آمار'))

    def validate_settings(self):
        """اعتبارسنجی تنظیمات پیش‌فرض"""
        self.stdout.write(self.style.SUCCESS('🔍 اعتبارسنجی تنظیمات پیش‌فرض...'))
        
        errors = SubscriptionManager.validate_default_settings()
        
        if not errors:
            self.stdout.write(self.style.SUCCESS('✅ تمام تنظیمات صحیح است'))
        else:
            self.stdout.write(self.style.ERROR('❌ خطاهای یافت شده:'))
            for error in errors:
                self.stdout.write(f'  • {error}')
        
        # نمایش تنظیمات فعلی
        self.stdout.write('\n📋 تنظیمات فعلی:')
        
        for setting in DefaultSubscriptionSettings.objects.all():
            status = '✅' if setting.is_active else '❌'
            self.stdout.write(
                f'  {status} {setting.get_setting_type_display()}: {setting.subscription_type.name}'
            )

    def setup_default_settings(self, plan_name=None, dry_run=False):
        """راه‌اندازی تنظیمات پیش‌فرض"""
        self.stdout.write(self.style.SUCCESS('⚙️ راه‌اندازی تنظیمات پیش‌فرض...'))
        
        if not plan_name:
            # جستجوی پلن Basic
            try:
                basic_plan = SubscriptionType.objects.get(name='Basic', is_active=True)
                plan_name = 'Basic'
            except SubscriptionType.DoesNotExist:
                # استفاده از اولین پلن رایگان
                free_plan = SubscriptionType.objects.filter(price=0, is_active=True).first()
                if free_plan:
                    plan_name = free_plan.name
                else:
                    raise CommandError('هیچ پلن مناسب برای تنظیم پیش‌فرض یافت نشد')
        
        try:
            subscription_type = SubscriptionType.objects.get(name=plan_name, is_active=True)
        except SubscriptionType.DoesNotExist:
            raise CommandError(f'پلن "{plan_name}" یافت نشد یا غیرفعال است')
        
        if dry_run:
            self.stdout.write(f'📋 پلن انتخابی: {subscription_type.name}')
            self.stdout.write('🔄 در حالت تست تغییراتی اعمال نمی‌شود')
            return
        
        # ایجاد یا به‌روزرسانی تنظیمات
        new_user_setting, created = DefaultSubscriptionSettings.objects.get_or_create(
            setting_type='new_user_default',
            defaults={
                'subscription_type': subscription_type,
                'is_active': True,
                'description': f'پلن پیش‌فرض برای کاربران جدید - تنظیم شده توسط دستور مدیریت'
            }
        )
        
        if not created:
            new_user_setting.subscription_type = subscription_type
            new_user_setting.is_active = True
            new_user_setting.save()
        
        fallback_setting, created = DefaultSubscriptionSettings.objects.get_or_create(
            setting_type='expired_fallback',
            defaults={
                'subscription_type': subscription_type,
                'is_active': True,
                'description': f'پلن fallback پس از انقضا - تنظیم شده توسط دستور مدیریت'
            }
        )
        
        if not created:
            fallback_setting.subscription_type = subscription_type
            fallback_setting.is_active = True
            fallback_setting.save()
        
        self.stdout.write(self.style.SUCCESS(f'✅ تنظیمات پیش‌فرض با پلن "{plan_name}" ایجاد شد'))

    def fix_users_without_subscription(self, dry_run=False):
        """رفع مشکل کاربران بدون اشتراک"""
        self.stdout.write(self.style.SUCCESS('🔧 رفع مشکل کاربران بدون اشتراک...'))
        
        # ابتدا اعتبارسنجی تنظیمات
        errors = SubscriptionManager.validate_default_settings()
        if errors:
            self.stdout.write(self.style.ERROR('❌ ابتدا تنظیمات پیش‌فرض را درست کنید:'))
            for error in errors:
                self.stdout.write(f'  • {error}')
            return
        
        users_without_subscription = User.objects.filter(subscription__isnull=True)
        total_users = users_without_subscription.count()
        
        if total_users == 0:
            self.stdout.write(self.style.SUCCESS('✅ همه کاربران اشتراک دارند'))
            return
        
        self.stdout.write(f'👥 تعداد کاربران بدون اشتراک: {total_users}')
        
        if dry_run:
            self.stdout.write('🔄 در حالت تست تغییراتی اعمال نمی‌شود')
            # نمایش چند کاربر نمونه
            sample_users = users_without_subscription[:5]
            self.stdout.write('📋 نمونه کاربران:')
            for user in sample_users:
                self.stdout.write(f'  - {user.name} ({user.phone_number}) - ثبت نام: {user.created_at}')
        else:
            success_count = 0
            for user in users_without_subscription:
                subscription = user.assign_default_subscription()
                if subscription:
                    success_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'✅ پایان رفع مشکل: {success_count}/{total_users} کاربر اشتراک دریافت کردند'
            ))

    def get_logging_level(self):
        """تنظیم سطح لاگ‌گیری"""
        return logging.INFO