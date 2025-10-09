import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.contrib.auth import get_user_model
from chatbot.models import Chatbot, ChatSession
from django.core.exceptions import ValidationError

# Get user
User = get_user_model()
user = User.objects.get(id=1)  # Assuming user with ID 1 exists

# Get chatbot
chatbot = Chatbot.objects.get(id=3)  # The chatbot from the error

print(f"User: {user}")
print(f"Chatbot: {chatbot}")
print(f"Chatbot is_active: {chatbot.is_active}")

# Try to create session manually
try:
    session = ChatSession(
        user=user,
        chatbot=chatbot,
        title="چت جدید"
    )
    session.full_clean()  # This will run all validations
    session.save()
    print("Session created successfully!")
    print(f"Session ID: {session.id}")
except ValidationError as e:
    print(f"ValidationError: {e}")
except Exception as e:
    print(f"Error: {e}")