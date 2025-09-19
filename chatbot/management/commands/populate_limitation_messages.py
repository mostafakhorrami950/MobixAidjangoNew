"""
Management command to populate default limitation messages
"""
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Populate default limitation messages'

    def handle(self, *args, **options):
        LimitationMessage = apps.get_model('chatbot', 'LimitationMessage')
        
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
                    self.style.SUCCESS(
                        f'Created limitation message: {limitation_message.limitation_type}'
                    )
                )
            else:
                # Update existing message if needed
                if (limitation_message.title != message_data['title'] or
                    limitation_message.message != message_data['message']):
                    limitation_message.title = message_data['title']
                    limitation_message.message = message_data['message']
                    limitation_message.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Updated limitation message: {limitation_message.limitation_type}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated limitation messages. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )