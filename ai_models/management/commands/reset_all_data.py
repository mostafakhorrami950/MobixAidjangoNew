from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Reset all data and repopulate with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )

    def handle(self, *args, **options):
        # Get models using apps.get_model
        AIModel = apps.get_model('ai_models', 'AIModel')
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        LimitationMessage = apps.get_model('chatbot', 'LimitationMessage')
        SidebarMenuItem = apps.get_model('chatbot', 'SidebarMenuItem')
        DefaultChatSettings = apps.get_model('chatbot', 'DefaultChatSettings')
        SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
        GlobalSettings = apps.get_model('core', 'GlobalSettings')
        TermsAndConditions = apps.get_model('core', 'TermsAndConditions')
        
        if not options['no_input']:
            confirm = input(
                "This will DELETE all existing data and repopulate with initial data.\n"
                "Are you sure you want to do this?\n"
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if confirm != 'yes':
                self.stdout.write("Reset cancelled.")
                return

        # Delete all existing data
        self.stdout.write("Deleting existing data...")
        
        # Delete in reverse order of dependencies
        DefaultChatSettings.objects.all().delete()
        SidebarMenuItem.objects.all().delete()
        LimitationMessage.objects.all().delete()
        Chatbot.objects.all().delete()
        AIModel.objects.all().delete()
        SubscriptionType.objects.all().delete()
        TermsAndConditions.objects.all().delete()
        # Note: We don't delete GlobalSettings as it should persist
        
        self.stdout.write("All existing data deleted successfully!")

        # Now repopulate with initial data
        self.stdout.write("=" * 60)
        self.stdout.write("Starting to repopulate with initial data...")
        
        # Run the populate all data command
        from .populate_all_data import Command as PopulateCommand
        populate_cmd = PopulateCommand()
        populate_cmd.stdout = self.stdout
        populate_cmd.style = self.style
        
        try:
            populate_cmd.handle()
        except Exception as e:
            self.stdout.write('❌ Error during data repopulation: {}'.format(e))
            import traceback
            traceback.print_exc()