#!/usr/bin/env python
"""
Test script to verify chat fixes are working correctly.
Run this script to check:
1. UTF-8 text encoding in database
2. Automatic title generation
3. Real-time streaming functionality
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixaidjangonew.settings')
django.setup()

from chatbot.models import ChatSession, ChatMessage, Chatbot
from ai_models.models import AIModel
from accounts.models import User
from ai_models.services import OpenRouterService


def test_utf8_encoding():
    """Test that UTF-8 text can be properly stored and retrieved"""
    print("🔤 Testing UTF-8 encoding...")
    
    # Test Persian/Arabic text
    test_texts = [
        "سلام! این یک تست است.", 
        "مرحبا، هذا اختبار.",
        "Hello! This is a test with emoji: 👋 🚀 💻",
        "Mixed text: English + فارسی + العربية"
    ]
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_utf8',
        defaults={'email': 'test@example.com', 'name': 'Test User'}
    )
    
    # Get a test chatbot
    chatbot = Chatbot.objects.filter(is_active=True).first()
    if not chatbot:
        print("❌ No active chatbot found. Please create one first.")
        return False
    
    # Create a test session
    session = ChatSession.objects.create(
        user=user,
        chatbot=chatbot,
        title="UTF-8 Test Session"
    )
    
    success = True
    
    for i, test_text in enumerate(test_texts):
        # Save message with UTF-8 text
        message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=test_text,
            tokens_count=10
        )
        
        # Retrieve and check
        retrieved_message = ChatMessage.objects.get(id=message.id)
        
        if retrieved_message.content == test_text:
            print(f"  ✅ Test {i+1}: '{test_text[:30]}...' - OK")
        else:
            print(f"  ❌ Test {i+1}: '{test_text[:30]}...' - FAILED")
            print(f"     Expected: {test_text}")
            print(f"     Got: {retrieved_message.content}")
            success = False
    
    # Cleanup
    session.delete()
    if created:
        user.delete()
    
    return success


def test_title_generation():
    """Test automatic title generation"""
    print("\n📝 Testing automatic title generation...")
    
    # Check if the view exists and works
    from chatbot.views import generate_chat_title
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    import json
    
    # Create a mock request
    factory = RequestFactory()
    
    # Get a test chatbot
    chatbot = Chatbot.objects.filter(is_active=True).first()
    if not chatbot:
        print("❌ No active chatbot found. Please create one first.")
        return False
    
    # Create test request data
    test_data = {
        'first_message': 'Hello, I need help with Python programming',
        'chatbot_id': chatbot.id
    }
    
    request = factory.post('/generate-title/', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    # Add a test user
    user, created = User.objects.get_or_create(
        username='test_title',
        defaults={'email': 'test@example.com', 'name': 'Test User'}
    )
    request.user = user
    
    try:
        response = generate_chat_title(request)
        
        if response.status_code == 200:
            data = json.loads(response.content)
            if 'title' in data and data['title']:
                print(f"  ✅ Title generation works: '{data['title']}'")
                success = True
            else:
                print("  ❌ Title generation failed: No title in response")
                success = False
        else:
            print(f"  ❌ Title generation failed: HTTP {response.status_code}")
            success = False
            
    except Exception as e:
        print(f"  ❌ Title generation failed: {str(e)}")
        success = False
    
    # Cleanup
    if created:
        user.delete()
    
    return success


def test_streaming_service():
    """Test the streaming service"""
    print("\n🔄 Testing streaming service...")
    
    # Get a test AI model
    ai_model = AIModel.objects.filter(is_active=True, model_type='text').first()
    if not ai_model:
        print("❌ No active text AI model found. Please create one first.")
        return False
    
    # Test the OpenRouter service
    service = OpenRouterService()
    
    # Simple test message
    messages = [
        {"role": "user", "content": "Say hello in Persian"}
    ]
    
    try:
        # Test streaming response
        response_generator = service.stream_text_response(ai_model, messages)
        
        if isinstance(response_generator, dict) and 'error' in response_generator:
            print(f"  ❌ Streaming failed: {response_generator['error']}")
            return False
        
        # Try to get first few chunks
        chunk_count = 0
        for chunk in response_generator:
            chunk_count += 1
            if chunk_count >= 3:  # Just test first few chunks
                break
        
        if chunk_count > 0:
            print(f"  ✅ Streaming works: Got {chunk_count} chunks")
            return True
        else:
            print("  ❌ Streaming failed: No chunks received")
            return False
            
    except Exception as e:
        print(f"  ❌ Streaming failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running Chat System Fixes Test Suite\n")
    
    results = []
    
    # Test UTF-8 encoding
    results.append(("UTF-8 Encoding", test_utf8_encoding()))
    
    # Test title generation
    results.append(("Title Generation", test_title_generation()))
    
    # Test streaming
    results.append(("Streaming Service", test_streaming_service()))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20} | {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("🎉 All tests passed! Your chat system fixes are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)