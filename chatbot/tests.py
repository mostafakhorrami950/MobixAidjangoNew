from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import ChatSession, UploadedFile
from ai_models.models import AIModel
from unittest.mock import patch, Mock
import json

User = get_user_model()

class FileUploadTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        
        # Create a test AI model
        self.ai_model = AIModel._default_manager.create(
            model_id='test-model',
            name='Test Model',
            is_active=True,
            is_free=True,
            model_type='text'
        )
        
        # Create a chat session
        self.session = ChatSession._default_manager.create(
            user=self.user,
            ai_model=self.ai_model,
            title='Test Session'
        )
        
        # Create an uploaded file
        self.uploaded_file = UploadedFile._default_manager.create(
            user=self.user,
            session=self.session,
            filename='test.txt',
            original_filename='test.txt',
            mimetype='text/plain',
            size=100
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_get_uploaded_files(self):
        """Test getting uploaded files for a session"""
        url = reverse('get_uploaded_files', kwargs={'session_id': self.session.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('files', data)
        self.assertEqual(len(data['files']), 1)
        self.assertEqual(data['files'][0]['original_filename'], 'test.txt')

    def test_delete_uploaded_file(self):
        """Test deleting an uploaded file"""
        url = reverse('delete_uploaded_file', kwargs={'file_id': self.uploaded_file.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        
        # Verify file is deleted from database
        with self.assertRaises(UploadedFile._default_manager.model.DoesNotExist):
            UploadedFile._default_manager.get(id=self.uploaded_file.id)

    def test_delete_uploaded_file_wrong_user(self):
        """Test that users can't delete other users' files"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            name='Other User'
        )
        
        # Create a file for the other user
        other_file = UploadedFile._default_manager.create(
            user=other_user,
            session=self.session,  # Same session but different user
            filename='other.txt',
            original_filename='other.txt',
            mimetype='text/plain',
            size=100
        )
        
        # Try to delete the other user's file
        url = reverse('delete_uploaded_file', kwargs={'file_id': other_file.id})
        response = self.client.delete(url)
        
        # Should return 404 since the file doesn't belong to the current user
        self.assertEqual(response.status_code, 404)