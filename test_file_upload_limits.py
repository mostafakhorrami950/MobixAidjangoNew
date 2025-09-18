import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from accounts.models import User
from subscriptions.models import SubscriptionType
from chatbot.models import FileUploadSettings
from chatbot.file_services import FileUploadService

# Create test subscription type
subscription_type, created = SubscriptionType.objects.get_or_create(
    name="Test Subscription",
    defaults={
        "description": "Test subscription for file upload limits",
        "price": 10000,
        "duration_days": 30,
        "sku": "TEST-SUB-001"
    }
)

# Create or update file upload settings for this subscription
file_settings, created = FileUploadSettings.objects.get_or_create(
    subscription_type=subscription_type,
    defaults={
        "max_file_size": 5 * 1024 * 1024,  # 5 MB
        "allowed_extensions": "txt,pdf,doc,docx",
        "max_files_per_chat": 3,
        "daily_file_limit": 5,
        "weekly_file_limit": 20,
        "monthly_file_limit": 50,
        "is_active": True
    }
)

# Create a test user
user, created = User.objects.get_or_create(
    phone_number="09123456789",
    defaults={
        "name": "Test User"
    }
)

# Test file extension check
print("Testing file extension check:")
result = FileUploadService.check_file_extension_allowed(subscription_type, "pdf")
print(f"PDF allowed: {result}")

result = FileUploadService.check_file_extension_allowed(subscription_type, "exe")
print(f"EXE allowed: {result}")

# Test file size check
print("\nTesting file size check:")
result, message = FileUploadService.check_file_size_limit(subscription_type, 3 * 1024 * 1024)  # 3 MB
print(f"3 MB file: {result}, {message}")

result, message = FileUploadService.check_file_size_limit(subscription_type, 10 * 1024 * 1024)  # 10 MB
print(f"10 MB file: {result}, {message}")

print("\nTest completed successfully!")