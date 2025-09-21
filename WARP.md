# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

MobixAI is a Django-based chatbot application featuring phone-based authentication, subscription management, and AI model integration. The system supports multiple AI models for text and image generation with sophisticated usage tracking and subscription-based access control.

## Common Development Commands

### Development Server
```bash
# Start development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080
```

### Database Management
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Database shell
python manage.py dbshell
```

### Initial Data Population
```bash
# Populate AI models (must run first)
python manage.py populate_models

# Populate subscription types
python manage.py populate_subscriptions

# Associate models with subscription types
python manage.py associate_models

# Populate default chatbots
python manage.py populate_chatbots

# Create default free subscription (if needed)
python manage.py create_default_free_subscription
```

### Maintenance Commands
```bash
# Check and handle expired subscriptions
python manage.py check_expired_subscriptions

# Reset monthly usage counters
python manage.py reset_monthly_usage

# Handle subscription renewals
python manage.py handle_subscription_renewals

# Reset premium tokens on subscription changes
python manage.py reset_premium_tokens_on_subscription_change
```

### Testing & Development
```bash
# Run Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check
```

## Architecture Overview

### Core Django Apps

**accounts** - User management with phone-based authentication
- Custom User model extending AbstractUser
- Phone number as primary identifier
- OTP-based verification system
- Automatic free subscription assignment

**ai_models** - AI model management and configuration
- Support for text and image generation models
- Integration with OpenRouter API
- Free vs subscription-based model access
- Web search settings configuration

**chatbot** - Chat functionality and session management
- Session-based conversation tracking
- Message history with token counting
- File upload capabilities with subscription limits
- Image processing and vision analysis support

**subscriptions** - Comprehensive subscription and usage management
- Multi-tier subscription system (Basic, Premium)
- Time-based usage limits (hourly, daily, weekly, monthly)
- Token and message counting
- Discount codes and financial transactions
- ZarinPal payment integration

**otp_service** - OTP generation and SMS integration
- IPANEL SMS service integration
- OTP verification and expiration handling

**core** - Shared utilities and base functionality
- Common URL routing
- Shared templates and static files

### Key Architectural Patterns

**Subscription-Based Access Control**
- Users automatically receive Basic (free) subscriptions
- AI models linked to subscription types through ModelSubscription
- Complex usage tracking with multiple time periods
- Automatic subscription expiration handling

**Session-Based Chat Management**
- ChatSession models group related conversations
- ChatMessage models store individual messages with token counts
- ChatSessionUsage tracks usage per session for accurate billing

**File Upload System**
- FileUploadSettings configure limits per subscription type
- UploadedFile tracks all file uploads with size and type validation
- Support for document processing (PDF, DOCX, Excel)

**Payment and Transaction System**
- FinancialTransaction models track all payment activities
- DiscountCode system with usage tracking
- ZarinPal integration for Iranian market

### Database Models Relationships

**User → UserSubscription → SubscriptionType**
- Each user has one active subscription
- Subscription types define usage limits and features

**AIModel → ModelSubscription → SubscriptionType**
- Many-to-many relationship defining model access per subscription

**ChatSession → ChatMessage**
- One-to-many relationship for conversation tracking
- Each message includes token count for billing

**User → UserUsage**
- Tracks usage across different time periods
- Separate tracking for free vs paid model usage

## Configuration

### Environment Variables
Key settings in `mobixai/settings.py`:
- `IPANEL_API_KEY` - SMS service API key
- `IPANEL_PATTERN_CODE` - OTP message template
- `OPENROUTER_API_KEY` - AI service API key
- `ZARINPAL_MERCHANT_ID` - Payment gateway ID

### API Integrations
- **IPANEL SMS**: OTP delivery via SMS
- **OpenRouter**: AI model access (GPT-4, Claude, DALL-E, etc.)
- **ZarinPal**: Payment processing for Iranian market

### Admin Interface
Access Django admin at `/admin/` to:
- Manage AI models and subscription associations
- Configure subscription types and usage limits
- Monitor user subscriptions and usage statistics
- Handle discount codes and financial transactions
- Configure chatbot system prompts

## Development Notes

### Custom Management Commands Location
- `ai_models/management/commands/` - Model management
- `subscriptions/management/commands/` - Subscription handling
- `chatbot/management/commands/` - Chatbot configuration

### Usage Tracking System
The system implements sophisticated usage tracking across multiple time periods:
- Real-time token and message counting
- Free vs paid model usage separation
- Time-based limits (hourly to monthly)
- Session-based usage recording for accuracy

### File Processing Capabilities
- PDF text extraction using PyPDF2
- DOCX document processing with python-docx
- Excel file handling with openpyxl
- Image analysis with vision-capable AI models

### Authentication Flow
1. User registers with phone number and name
2. OTP sent via IPANEL SMS service
3. OTP verification activates account
4. Automatic Basic subscription assignment
5. Session-based authentication for chat access

## URL Structure
- `/` - Core application (redirects to chat)
- `/accounts/` - Registration, login, OTP verification
- `/chat/` - Chat interface and session management  
- `/subscriptions/` - Payment and subscription management
- `/admin/` - Django admin interface

## Key Dependencies
- **Django 5.1.2** - Web framework
- **psycopg2-binary** - PostgreSQL adapter (configured for SQLite in development)
- **requests** - HTTP client for API calls
- **python-decouple** - Environment configuration
- **zarinpal** - Payment gateway integration
- **PyPDF2, python-docx, openpyxl** - File processing