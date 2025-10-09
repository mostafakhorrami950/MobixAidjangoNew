# MobixAI API Specification

## Overview
This document provides a technical specification for the MobixAI API endpoints. All endpoints follow REST conventions and return JSON responses.

## Authentication
All endpoints require session-based authentication. Clients must include valid session cookies with each request.

## Base URL
`/api/`

## Response Format
All successful responses are returned as JSON. Error responses follow this format:
```json
{
  "error": "Error message"
}
```

## Pagination
List endpoints support pagination with the following query parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

Paginated responses include:
```json
{
  "count": 100,
  "next": "http://example.com/api/resource/?page=2",
  "previous": null,
  "results": [
    // ... items
  ]
}
```

## Endpoints

### Users

#### Get Current User
```
GET /api/users/
```

**Response:**
```json
[
  {
    "id": 1,
    "phone_number": "+1234567890",
    "name": "John Doe",
    "is_verified": true,
    "date_joined": "2023-01-01T00:00:00Z"
  }
]
```

#### Get User Subscription
```
GET /api/users/subscription/
```

**Response (Success):**
```json
{
  "id": 1,
  "subscription_type": {
    "id": 1,
    "name": "Premium",
    "description": "Premium subscription",
    "price": "99.99",
    "duration_days": 30,
    "sku": "PREMIUM-001",
    "max_tokens": 100000,
    "max_tokens_free": 0,
    "max_openrouter_cost_usd": "10.00",
    "hourly_max_messages": 100,
    "hourly_max_tokens": 50000,
    "three_hours_max_messages": 200,
    "three_hours_max_tokens": 100000,
    "twelve_hours_max_messages": 500,
    "twelve_hours_max_tokens": 250000,
    "daily_max_messages": 1000,
    "daily_max_tokens": 500000,
    "weekly_max_messages": 5000,
    "weekly_max_tokens": 2500000,
    "monthly_max_messages": 20000,
    "monthly_max_tokens": 10000000,
    "monthly_free_model_messages": 0,
    "monthly_free_model_tokens": 0,
    "daily_image_generation_limit": 50,
    "weekly_image_generation_limit": 250,
    "monthly_image_generation_limit": 1000,
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z"
  },
  "is_active": true,
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2023-02-01T00:00:00Z"
}
```

**Response (No Subscription):**
```json
{
  "detail": "No active subscription found"
}
```

### Chatbots

#### List Chatbots
```
GET /api/chatbots/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "General Assistant",
    "description": "A general purpose AI assistant",
    "image": "/media/chatbot_images/general.png",
    "is_active": true,
    "system_prompt": "You are a helpful assistant.",
    "chatbot_type": "text"
  }
]
```

### AI Models

#### List AI Models
```
GET /api/ai-models/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "GPT-4",
    "model_id": "openai/gpt-4",
    "description": "Most capable GPT-4 model",
    "model_type": "text",
    "is_active": true,
    "is_free": false,
    "token_cost_multiplier": "1.00"
  }
]
```

### Chat Sessions

#### List Chat Sessions
```
GET /api/chat-sessions/
```

**Response:**
```json
[
  {
    "id": 1,
    "chatbot": {
      "id": 1,
      "name": "General Assistant",
      "description": "A general purpose AI assistant",
      "image": "/media/chatbot_images/general.png",
      "is_active": true,
      "system_prompt": "You are a helpful assistant.",
      "chatbot_type": "text"
    },
    "ai_model": {
      "id": 1,
      "name": "GPT-4",
      "model_id": "openai/gpt-4",
      "description": "Most capable GPT-4 model",
      "model_type": "text",
      "is_active": true,
      "is_free": false,
      "token_cost_multiplier": "1.00"
    },
    "title": "New Chat",
    "auto_generate_title": true,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "is_active": true
  }
]
```

#### Create Chat Session
```
POST /api/chat-sessions/
```

**Request Body:**
```json
{
  "chatbot_id": 1,
  "ai_model_id": "openai/gpt-4",
  "title": "New Chat"
}
```

**Response (Success):**
```json
{
  "id": 1,
  "chatbot": {
    "id": 1,
    "name": "General Assistant",
    "description": "A general purpose AI assistant",
    "image": "/media/chatbot_images/general.png",
    "is_active": true,
    "system_prompt": "You are a helpful assistant.",
    "chatbot_type": "text"
  },
  "ai_model": {
    "id": 1,
    "name": "GPT-4",
    "model_id": "openai/gpt-4",
    "description": "Most capable GPT-4 model",
    "model_type": "text",
    "is_active": true,
    "is_free": false,
    "token_cost_multiplier": "1.00"
  },
  "title": "New Chat",
  "auto_generate_title": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "is_active": true
}
```

**Response (Error):**
```json
{
  "error": "Error message"
}
```

#### Get Chat Session
```
GET /api/chat-sessions/{id}/
```

**Response:**
```json
{
  "id": 1,
  "chatbot": {
    "id": 1,
    "name": "General Assistant",
    "description": "A general purpose AI assistant",
    "image": "/media/chatbot_images/general.png",
    "is_active": true,
    "system_prompt": "You are a helpful assistant.",
    "chatbot_type": "text"
  },
  "ai_model": {
    "id": 1,
    "name": "GPT-4",
    "model_id": "openai/gpt-4",
    "description": "Most capable GPT-4 model",
    "model_type": "text",
    "is_active": true,
    "is_free": false,
    "token_cost_multiplier": "1.00"
  },
  "title": "New Chat",
  "auto_generate_title": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "is_active": true
}
```

#### Update Chat Session
```
PUT /api/chat-sessions/{id}/
```

**Request Body:**
```json
{
  "title": "Updated Chat Title"
}
```

**Response:**
```json
{
  "id": 1,
  "chatbot": {
    "id": 1,
    "name": "General Assistant",
    "description": "A general purpose AI assistant",
    "image": "/media/chatbot_images/general.png",
    "is_active": true,
    "system_prompt": "You are a helpful assistant.",
    "chatbot_type": "text"
  },
  "ai_model": {
    "id": 1,
    "name": "GPT-4",
    "model_id": "openai/gpt-4",
    "description": "Most capable GPT-4 model",
    "model_type": "text",
    "is_active": true,
    "is_free": false,
    "token_cost_multiplier": "1.00"
  },
  "title": "Updated Chat Title",
  "auto_generate_title": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:01:00Z",
  "is_active": true
}
```

#### Delete Chat Session
```
DELETE /api/chat-sessions/{id}/
```

**Response:**
```json
{
  "success": true
}
```

#### Get Session Messages
```
GET /api/chat-sessions/{id}/messages/
```

**Response:**
```json
{
  "messages": [
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440000",
      "message_type": "user",
      "content": "Hello, how are you?",
      "tokens_count": 10,
      "image_url": "",
      "created_at": "2023-01-01T00:00:00Z",
      "edited_at": null,
      "disabled": false
    },
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440001",
      "message_type": "assistant",
      "content": "I'm doing well, thank you for asking!",
      "tokens_count": 15,
      "image_url": "",
      "created_at": "2023-01-01T00:00:01Z",
      "edited_at": null,
      "disabled": false
    }
  ]
}
```

#### Send Message to Session
```
POST /api/chat-sessions/{id}/send/
```

**Request Body:**
```json
{
  "message": "Hello, how are you?"
}
```

**Response (Success):**
```json
{
  "user_message": {
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "message_type": "user",
    "content": "Hello, how are you?",
    "tokens_count": 10,
    "image_url": "",
    "created_at": "2023-01-01T00:00:00Z",
    "edited_at": null,
    "disabled": false
  }
}
```

**Response (Error):**
```json
{
  "error": "Error message"
}
```

#### Update Session Title
```
POST /api/chat-sessions/{id}/update-title/
```

**Request Body:**
```json
{
  "title": "New Chat Title"
}
```

**Response:**
```json
{
  "success": true,
  "title": "New Chat Title"
}
```

#### Edit Message
```
POST /api/chat-sessions/{id}/messages/{message_id}/edit/
```

**Request Body:**
```json
{
  "content": "Updated message content"
}
```

**Response (Success):**
```json
{
  "success": true,
  "disabled_message_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Response (Error):**
```json
{
  "error": "Error message"
}
```

### Chat Session Usage

#### List Chat Session Usage
```
GET /api/chat-session-usages/
```

**Response:**
```json
[
  {
    "id": 1,
    "tokens_count": 1000,
    "free_model_tokens_count": 0,
    "is_free_model": false,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

## Error Responses

All endpoints can return the following HTTP status codes:

- `200 OK` - Successful GET, PUT, PATCH, or DELETE request
- `201 Created` - Successful POST request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses follow this format:
```json
{
  "error": "Detailed error message"
}
```

## Rate Limiting

The API implements the same rate limiting as the existing application:
- Time-based restrictions (hourly, daily, weekly, monthly)
- Token counting and limits
- Usage tracking per subscription type

## Business Logic Implementation

The API endpoints implement the exact same business logic as the existing Django views:

1. **User Authentication**: Session-based authentication using the existing CustomUser model
2. **Subscription Management**: Access control based on user subscriptions
3. **Usage Limits**: All time-based and token-based limits are enforced
4. **AI Model Access**: Model access controlled through subscription relationships
5. **Message Handling**: Token counting and message processing follows existing logic
6. **Chat Session Management**: Session lifecycle management matches existing implementation

## Integration Guidelines

### For Mobile Applications
1. Implement session-based authentication
2. Store session cookies securely
3. Handle pagination for list endpoints
4. Implement proper error handling

### For Web Applications
1. Use existing Django session authentication
2. Make AJAX requests to API endpoints
3. Handle CSRF tokens for POST/PUT/DELETE requests

### For Telegram Bots
1. Implement a login flow to obtain session cookies
2. Store session cookies for subsequent requests
3. Use API endpoints to create sessions and send/receive messages

## Testing

The API can be tested using:
1. The browsable API interface at `/api/`
2. Command-line tools like curl
3. API testing tools like Postman
4. Custom test scripts

## Security Considerations

1. All endpoints require authentication
2. CSRF protection is enforced for state-changing operations
3. Session cookies must be transmitted securely (HTTPS)
4. Input validation is performed on all request data
5. Rate limiting prevents abuse

## Performance Considerations

1. Pagination is implemented for list endpoints
2. Database queries are optimized through Django ORM
3. Caching strategies follow existing application patterns
4. Response data is minimized to essential fields only