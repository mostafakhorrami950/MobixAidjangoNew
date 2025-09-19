from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
import os

class Command(BaseCommand):
    help = 'تشخیص و حل مشکلات فایل‌های استاتیک Django'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 شروع تشخیص مشکلات فایل‌های استاتیک...'))
        
        # بررسی تنظیمات کلی
        self.check_static_settings()
        
        # بررسی مسیرها
        self.check_static_paths()
        
        # بررسی فایل‌های ادمین
        self.check_admin_static_files()
        
        # بررسی فایل‌های پروژه
        self.check_project_static_files()
        
        self.stdout.write(self.style.SUCCESS('✅ بررسی تکمیل شد!'))

    def check_static_settings(self):
        self.stdout.write(self.style.WARNING('📋 بررسی تنظیمات فایل‌های استاتیک:'))
        
        # STATIC_URL
        self.stdout.write(f'  STATIC_URL: {settings.STATIC_URL}')
        
        # STATIC_ROOT
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            self.stdout.write(f'  STATIC_ROOT: {settings.STATIC_ROOT}')
            if os.path.exists(settings.STATIC_ROOT):
                self.stdout.write(self.style.SUCCESS('    ✅ مسیر STATIC_ROOT موجود است'))
            else:
                self.stdout.write(self.style.ERROR('    ❌ مسیر STATIC_ROOT موجود نیست'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️ STATIC_ROOT تنظیم نشده'))
        
        # STATICFILES_DIRS
        if hasattr(settings, 'STATICFILES_DIRS'):
            self.stdout.write(f'  STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
            for static_dir in settings.STATICFILES_DIRS:
                if os.path.exists(static_dir):
                    self.stdout.write(self.style.SUCCESS(f'    ✅ {static_dir} موجود است'))
                else:
                    self.stdout.write(self.style.ERROR(f'    ❌ {static_dir} موجود نیست'))
        
        # DEBUG mode
        self.stdout.write(f'  DEBUG: {settings.DEBUG}')
        
        # STATICFILES_STORAGE
        if hasattr(settings, 'STATICFILES_STORAGE'):
            self.stdout.write(f'  STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}')

    def check_static_paths(self):
        self.stdout.write(self.style.WARNING('\n📁 بررسی مسیرهای فایل‌های استاتیک:'))
        
        # بررسی مسیر static در پروژه
        static_path = os.path.join(settings.BASE_DIR, 'static')
        if os.path.exists(static_path):
            self.stdout.write(self.style.SUCCESS(f'  ✅ {static_path} موجود است'))
            # فهرست فایل‌ها
            files = []
            for root, dirs, filenames in os.walk(static_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            self.stdout.write(f'    تعداد فایل‌ها: {len(files)}')
        else:
            self.stdout.write(self.style.ERROR(f'  ❌ {static_path} موجود نیست'))

    def check_admin_static_files(self):
        self.stdout.write(self.style.WARNING('\n👤 بررسی فایل‌های استاتیک ادمین:'))
        
        # فایل‌های کلیدی ادمین
        admin_files = [
            'admin/css/base.css',
            'admin/css/dashboard.css', 
            'admin/js/core.js',
            'admin/js/admin/RelatedObjectLookups.js',
        ]
        
        for file_path in admin_files:
            found = finders.find(file_path)
            if found:
                self.stdout.write(self.style.SUCCESS(f'  ✅ {file_path} یافت شد: {found}'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ {file_path} یافت نشد'))

    def check_project_static_files(self):
        self.stdout.write(self.style.WARNING('\n🎨 بررسی فایل‌های استاتیک پروژه:'))
        
        # بررسی فایل‌های CSS پروژه
        css_files = [
            'css/navigation.css',
            'css/auth-forms.css', 
            'css/home.css',
            'css/purchase.css',
            'css/chat.css',
        ]
        
        for file_path in css_files:
            found = finders.find(file_path)
            if found:
                self.stdout.write(self.style.SUCCESS(f'  ✅ {file_path} یافت شد: {found}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ {file_path} یافت نشد'))

    def add_arguments(self, parser):
        parser.add_argument(
            '--collect',
            action='store_true',
            help='اجرای collectstatic پس از بررسی',
        )
        
        if self.options.get('collect'):
            self.stdout.write(self.style.SUCCESS('\n🔄 اجرای collectstatic...'))
            from django.core.management import call_command
            call_command('collectstatic', '--noinput')
            self.stdout.write(self.style.SUCCESS('✅ collectstatic تکمیل شد'))