from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Populate default sidebar menu items'

    def handle(self, *args, **options):
        SidebarMenuItem = apps.get_model('chatbot', 'SidebarMenuItem')
        
        # Clear existing items first
        SidebarMenuItem.objects.all().delete()
        
        # Default menu items
        default_items = [
            {
                'name': 'چت',
                'url_name': 'chatbot:chat',
                'icon_class': 'fas fa-comments',
                'order': 1,
                'show_only_for_authenticated': True,
            },
            {
                'name': 'داشبورد',
                'url_name': 'dashboard',
                'icon_class': 'fas fa-tachometer-alt',
                'order': 10,
                'show_only_for_authenticated': True,
            },
            {
                'name': 'تراکنش‌های مالی',
                'url_name': 'financial_transactions',
                'icon_class': 'fas fa-credit-card',
                'order': 11,
                'show_only_for_authenticated': True,
            },
            {
                'name': 'خرید اشتراک',
                'url_name': 'purchase_subscription',
                'icon_class': 'fas fa-shopping-cart',
                'order': 12,
                'show_only_for_authenticated': True,
            },
            {
                'name': 'پروفایل',
                'url_name': 'profile',
                'icon_class': 'fas fa-user',
                'order': 13,
                'show_only_for_authenticated': True,
            },
            {
                'name': 'خروج',
                'url_name': 'accounts:logout',
                'icon_class': 'fas fa-sign-out-alt',
                'order': 14,
                'show_only_for_authenticated': True,
            },
            {
                'name': 'ورود',
                'url_name': 'accounts:login',
                'icon_class': 'fas fa-sign-in-alt',
                'order': 1,
                'show_only_for_non_authenticated': True,
            },
        ]
        
        # Create menu items
        for item_data in default_items:
            item = SidebarMenuItem.objects.create(**item_data)
            self.stdout.write(
                self.style.SUCCESS(f'Created menu item: {item.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated {len(default_items)} menu items')
        )