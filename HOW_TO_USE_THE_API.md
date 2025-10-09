# How to Use the MobixAI API

This document explains how to use the newly created Django REST Framework (DRF) API for the MobixAI project.

## Overview

The API provides RESTful endpoints for all the functionality of the MobixAI application while maintaining the exact same business logic as the existing Django views. The API can be used for building:
- Telegram bots
- Android applications
- iOS applications
- Web applications
- Desktop applications

## Prerequisites

1. The API requires Django REST Framework to be installed:
   ```bash
   pip install djangorestframework
   ```

2. The following changes have already been made to the project:
   - Added `rest_framework` and `api` to `INSTALLED_APPS` in `settings.py`
   - Added DRF configuration to `settings.py`
   - Added `djangorestframework>=3.14.0` to `requirements.txt`
   - Added `/api/` URL pattern to main `urls.py`

## Authentication

All API endpoints require authentication via session authentication. Users must be logged in to access any API endpoints.

For external applications (like Telegram bots or mobile apps), you'll need to implement a login flow:
1. Send a POST request to your existing login endpoint with user credentials
2. Store the session cookies from the response
3. Include those cookies in all subsequent API requests

## Available Endpoints

### Base URL
All endpoints are prefixed with `/api/`

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

## Example Usage

### 1. Get User Information
```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -b "sessionid=your_session_id;csrftoken=your_csrf_token"
```

### 2. List Available Chatbots
```bash
curl -X GET http://localhost:8000/api/chatbots/ \
  -H "Content-Type: application/json" \
  -b "sessionid=your_session_id;csrftoken=your_csrf_token"
```

### 3. Create a New Chat Session
```bash
curl -X POST http://localhost:8000/api/chat-sessions/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your_csrf_token" \
  -b "sessionid=your_session_id;csrftoken=your_csrf_token" \
  -d '{
    "chatbot_id": 1,
    "ai_model_id": "openai/gpt-4",
    "title": "New Chat"
  }'
```

### 4. Send a Message to a Chat Session
```bash
curl -X POST http://localhost:8000/api/chat-sessions/1/send/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your_csrf_token" \
  -b "sessionid=your_session_id;csrftoken=your_csrf_token" \
  -d '{
    "message": "Hello, how are you?"
  }'
```

## Business Logic Consistency

The API implementation maintains exact consistency with the existing Django views:

1. **User Authentication**: Uses the same CustomUser model with phone_number as USERNAME_FIELD
2. **Subscription Management**: Respects the same subscription-based access control
3. **Usage Limits**: Implements all usage limit checks exactly as in the existing system:
   - Time-based restrictions (hourly, daily, weekly, monthly)
   - Token counting and limits
   - Free model usage tracking
   - Image generation limits
4. **AI Model Access**: Controls access through the same ModelSubscription and UserSubscription relationships
5. **Message Handling**: Follows the same logic for message creation, editing, and token counting
6. **Chat Session Management**: Works exactly as the existing session creation, title generation, and message management

## Testing the API

You can test the API using the provided test scripts:

1. `simple_api_test.py` - Tests that the API components can be imported correctly
2. `test_api.py` - More comprehensive tests (requires a working Django test environment)

To run the simple test:
```bash
python simple_api_test.py
```

## Integration with External Applications

### For Telegram Bots
1. Implement a login flow to obtain session cookies
2. Store the session cookies for subsequent requests
3. Use the API endpoints to create sessions, send messages, and retrieve responses

### For Mobile Applications
1. Implement a login flow to obtain session cookies
2. Store the session cookies securely
3. Use the API endpoints to provide chat functionality in your app

### For Web Applications
1. Use the existing Django session authentication
2. Make AJAX requests to the API endpoints
3. Handle responses in your frontend code

## Error Handling

The API returns standard HTTP status codes:
- 200: Success
- 201: Created (for POST requests that create resources)
- 400: Bad Request (invalid input)
- 401: Unauthorized (not logged in)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 500: Internal Server Error (unexpected error)

Error responses include a JSON object with an error message:
```json
{
  "error": "Detailed error message"
}
```

## Support for Pagination

List endpoints support pagination:
- `GET /api/chat-sessions/?page=1&page_size=20`

The response includes pagination information:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/chat-sessions/?page=2&page_size=20",
  "previous": null,
  "results": [
    // ... array of objects
  ]
}
```

## Conclusion

The MobixAI API provides a clean, RESTful interface to all the functionality of the application while maintaining complete compatibility with the existing business logic. It can be used to build a wide variety of applications that need to interact with the MobixAI platform.