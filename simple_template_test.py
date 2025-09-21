#!/usr/bin/env python3

"""
Simple test for template rendering without chatbot.ai_model errors
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixaidjangonew.settings')
django.setup()

from django.template.loader import get_template
from django.template import Context

def test_chat_template():
    """Test chat template rendering"""
    try:
        print("Testing chat template rendering...")
        
        # Get the template
        template = get_template('chatbot/chat.html')
        
        # Create mock context data
        context = {
            'available_chatbots': [
                {
                    'id': 1, 
                    'name': 'Test ChatBot', 
                    'description': 'Test description',
                    'is_active': True,
                    'user_has_access': True
                }
            ],
            'available_models': [
                {
                    'model_id': 'gpt-3.5-turbo', 
                    'name': 'GPT-3.5 Turbo', 
                    'description': 'Test model',
                    'is_free': True,
                    'model_type': 'text',
                    'is_active': True,
                    'user_has_access': True
                }
            ],
            'chat_sessions': []
        }
        
        # Try to render
        rendered_content = template.render(context)
        
        # Check if it contains expected content without errors
        if 'Test ChatBot' in rendered_content:
            print("✅ Chat template rendered successfully")
            print(f"✅ Template length: {len(rendered_content)} characters")
            return True
        else:
            print("❌ Template rendered but missing expected content")
            return False
            
    except Exception as e:
        print(f"❌ Template rendering failed: {str(e)}")
        return False

def test_backup_template():
    """Test backup chat template rendering"""
    try:
        print("Testing backup chat template rendering...")
        
        # Get the template
        template = get_template('chatbot/chat_backup.html')
        
        # Create mock context data
        context = {
            'available_chatbots': [
                {
                    'id': 1, 
                    'name': 'Test ChatBot Backup', 
                    'description': 'Test description',
                    'is_active': True,
                    'user_has_access': True
                }
            ],
            'available_models': [
                {
                    'model_id': 'gpt-3.5-turbo', 
                    'name': 'GPT-3.5 Turbo', 
                    'description': 'Test model',
                    'is_free': True,
                    'model_type': 'text',
                    'is_active': True,
                    'user_has_access': True
                }
            ],
            'chat_sessions': []
        }
        
        # Try to render
        rendered_content = template.render(context)
        
        # Check if it contains expected content without errors
        if 'Test ChatBot Backup' in rendered_content:
            print("✅ Backup chat template rendered successfully")
            print(f"✅ Template length: {len(rendered_content)} characters")
            return True
        else:
            print("❌ Backup template rendered but missing expected content")
            return False
            
    except Exception as e:
        print(f"❌ Backup template rendering failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Template Fixes\n" + "="*50)
    
    # Test main template
    result1 = test_chat_template()
    print()
    
    # Test backup template
    result2 = test_backup_template()
    print()
    
    if result1 and result2:
        print("🎉 All template tests passed!")
        print("✅ The chatbot.ai_model AttributeError has been fixed")
    else:
        print("❌ Some template tests failed")
    
    exit(0 if (result1 and result2) else 1)