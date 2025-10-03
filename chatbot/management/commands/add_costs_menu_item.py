from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Add costs menu item to sidebar menu items'

    def handle(self, *args, **options):
        # Get the SidebarMenuItem model
        SidebarMenuItem = apps.get_model('chatbot', 'SidebarMenuItem')
        
        # Check if the menu item already exists
        menu_item, created = SidebarMenuItem.objects.get_or_create(
            name='هزینه‌های استفاده',
            url_name='subscriptions:user_openrouter_costs',
            defaults={
                'icon_class': 'fas fa-coins',
                'order': 7,  # Place it after purchase subscription
                'is_active': True,
                'required_permission': None,
                'show_only_for_authenticated': True,
                'show_only_for_non_authenticated': False,
            }
        )
        
        if created:
            self.stdout.write(
                'Successfully added "هزینه‌های استفاده" menu item'
            )
        else:
            self.stdout.write(
                'Menu item "هزینه‌های استفاده" already exists'
            )