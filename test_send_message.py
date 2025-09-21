import os
import django
import json
from django.apps import apps
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from chatbot.views import send_message
from django.contrib.auth import get_user

def test_send_message_comprehensive_check():
    # Create a request factory
    factory = RequestFactory()
    
    # Get a test user and session
    try:
        User = apps.get_model('accounts', 'User')
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        
        user = User.objects.first()
        session = ChatSession.objects.first()
        
        if not user or not session:
            print("No user or session found in database")
            return
            
        print(f"Testing with user: {user.name}")
        print(f"Testing with session: {session.id}")
        
        # Create a mock request
        request = factory.post(f'/chat/send_message/{session.id}/', 
                              data=json.dumps({'message': 'Test message'}),
                              content_type='application/json')
        
        # Add user to request (simulate authentication)
        from django.utils.functional import SimpleLazyObject
        request.user = SimpleLazyObject(lambda: user)
        
        # Call the send_message view
        response = send_message(request, session.id)
        print(f"Response status code: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Response content: {response.content.decode('utf-8')}")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_send_message_comprehensive_check()