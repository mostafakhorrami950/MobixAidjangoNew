# API Endpoints Documentation

## Authentication
All endpoints require authentication via session authentication. Users must be logged in to access any API endpoints.

## Base URL
All endpoints are prefixed with `/api/`

## Users

### Get Current User
```
GET /api/users/
```

**Response:**
```json
{
    "id": 1,
    "phone_number": "+1234567890",
    "name": "John Doe",
    "is_verified": true,
    "date_joined": "2023-01-01T00:00:00Z"
}
```

### Get User Subscription
```
GET /api/users/subscription/
```

**Response:**
```json
{
    "id": 1,
    "subscription_type": {
        "id": 1,
        "name": "Premium",
        "description": "Premium subscription with all features",
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

## Chatbots

### List Available Chatbots
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

## AI Models

### List Available AI Models
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

## Chat Sessions

### List Chat Sessions
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

### Create Chat Session
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

### Get Chat Session
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

### Update Chat Session
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

### Delete Chat Session
```
DELETE /api/chat-sessions/{id}/
```

**Response:**
```json
{
    "success": true
}
```

### Get Session Messages
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

### Send Message to Session
```
POST /api/chat-sessions/{id}/send/
```

**Request Body:**
```json
{
    "message": "Hello, how are you?"
}
```

**Response:**
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

### Update Session Title
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

### Edit Message
```
POST /api/chat-sessions/{id}/messages/{message_id}/edit/
```

**Request Body:**
```json
{
    "content": "Updated message content"
}
```

**Response:**
```json
{
    "success": true,
    "disabled_message_ids": [
        "550e8400-e29b-41d4-a716-446655440001",
        "550e8400-e29b-41d4-a716-446655440002"
    ]
}
```

## Chat Session Usage

### List Chat Session Usage
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