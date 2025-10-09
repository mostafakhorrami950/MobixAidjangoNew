# MobixAI API

This is the Django REST Framework (DRF) API for the MobixAI project. It provides RESTful endpoints for all the functionality of the application while maintaining the exact same business logic as the existing Django views.

## API Endpoints

### Authentication
All endpoints require authentication via session authentication.

### Users
- `GET /api/users/` - Get current user information
- `GET /api/users/subscription/` - Get user's subscription information

### Chatbots
- `GET /api/chatbots/` - List available chatbots for the current user

### AI Models
- `GET /api/ai-models/` - List available AI models for the current user

### Chat Sessions
- `GET /api/chat-sessions/` - List user's chat sessions
- `POST /api/chat-sessions/` - Create a new chat session
- `GET /api/chat-sessions/{id}/` - Get a specific chat session
- `PUT /api/chat-sessions/{id}/` - Update a chat session
- `DELETE /api/chat-sessions/{id}/` - Delete a chat session
- `GET /api/chat-sessions/{id}/messages/` - Get messages for a chat session
- `POST /api/chat-sessions/{id}/send/` - Send a message to a chat session
- `POST /api/chat-sessions/{id}/update-title/` - Update session title
- `POST /api/chat-sessions/{id}/messages/{message_id}/edit/` - Edit a message

### Chat Session Usage
- `GET /api/chat-session-usages/` - List user's chat session usage records

## Business Logic Implementation

This API follows the exact same business logic as the existing Django views:

1. **User Authentication**: All endpoints require authentication and use the same CustomUser model with phone_number as the USERNAME_FIELD.

2. **Subscription Management**: The API respects the same subscription-based access control as the existing system.

3. **Usage Limits**: All usage limit checks are implemented exactly as in the existing system:
   - Time-based restrictions (hourly, daily, weekly, monthly)
   - Token counting and limits
   - Free model usage tracking
   - Image generation limits

4. **AI Model Access**: Access to AI models is controlled through the same ModelSubscription and UserSubscription relationships.

5. **Message Handling**: Message creation, editing, and token counting follows the same logic as the existing system.

6. **Chat Session Management**: Session creation, title generation, and message management work exactly as in the existing system.

## Installation

1. Add `rest_framework` and `api` to INSTALLED_APPS in settings.py
2. Add DRF settings to settings.py:
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.SessionAuthentication',
       ],
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ],
       'DEFAULT_RENDERER_CLASSES': [
           'rest_framework.renderers.JSONRenderer',
       ],
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 20
   }
   ```
3. Add to requirements.txt:
   ```
   djangorestframework>=3.14.0
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```

## Usage

The API can be used for building:
- Telegram bots
- Android applications
- iOS applications
- Web applications
- Desktop applications

All endpoints return data in JSON format and maintain the same structure and business rules as the existing Django application.