# Image Generation and Message Sending Limitations Report

## Overview

This report documents the comprehensive validation system implemented for image generation and message sending limitations in the MobixAI platform. The system ensures that all user interactions with the API are properly validated against admin-configured limits before any resource consumption occurs.

## Implemented Limitations

### 1. Image Generation Limits

All image generation requests are validated against subscription-based limits:

#### Daily Limits
- **Configuration**: `daily_image_generation_limit` field in `SubscriptionType` model
- **Default**: 10 images per day
- **Validation**: Checked in `UsageService.check_image_generation_limit()`
- **Reset**: Daily at midnight (00:00)

#### Weekly Limits
- **Configuration**: `weekly_image_generation_limit` field in `SubscriptionType` model
- **Default**: 50 images per week
- **Validation**: Checked in `UsageService.check_image_generation_limit()`
- **Reset**: Weekly on Monday at midnight

#### Monthly Limits
- **Configuration**: `monthly_image_generation_limit` field in `SubscriptionType` model
- **Default**: 200 images per month
- **Validation**: Checked in `UsageService.check_image_generation_limit()`
- **Reset**: Monthly on the 1st at midnight

### 2. Message Sending Limits

Message sending is validated against time-based restrictions:

#### Hourly Message Limits
- **Configuration**: `hourly_max_messages` field in `SubscriptionType` model
- **Default**: 0 (unlimited)
- **Validation**: Checked in `MessageValidationService._check_hourly_message_limit()`

#### Daily Message Limits
- **Configuration**: `daily_max_messages` field in `SubscriptionType` model
- **Default**: 0 (unlimited)
- **Validation**: Part of `UsageService.comprehensive_check()`

### 3. Token Consumption Limits

Token usage is monitored and limited across multiple time periods:

#### Hourly Token Limits
- **Configuration**: `hourly_max_tokens` field in `SubscriptionType` model
- **Default**: 0 (unlimited)
- **Validation**: Checked in `MessageValidationService._check_hourly_token_limit()`

#### Daily Token Limits
- **Configuration**: `daily_max_tokens` field in `SubscriptionType` model
- **Default**: 0 (unlimited)
- **Validation**: Checked in `MessageValidationService._check_daily_token_limit()`

#### Weekly Token Limits
- **Configuration**: `weekly_max_tokens` field in `SubscriptionType` model
- **Default**: 0 (unlimited)
- **Validation**: Part of `UsageService.comprehensive_check()`

#### Monthly Token Limits
- **Configuration**: `monthly_max_tokens` field in `SubscriptionType` model
- **Default**: 0 (unlimited)
- **Validation**: Part of `UsageService.comprehensive_check()`

#### Free Model Token Limits
- **Configuration**: `max_tokens_free` and `monthly_free_model_tokens` fields
- **Validation**: Part of `UsageService.comprehensive_check()`

### 4. OpenRouter Cost Limits

API cost consumption is limited per subscription:

#### Cost Limit
- **Configuration**: `max_openrouter_cost_usd` field in `SubscriptionType` model
- **Default**: 0 (unlimited)
- **Validation**: Checked in `UsageService.check_openrouter_cost_limit()`

### 5. File Upload Limits

File operations are validated against subscription-based restrictions:

#### Daily File Upload Limits
- **Configuration**: `daily_file_limit` field in `FileUploadSettings` model
- **Validation**: Checked in `FileUploadService.check_file_upload_limit()`

#### Weekly File Upload Limits
- **Configuration**: `weekly_file_limit` field in `FileUploadSettings` model
- **Validation**: Checked in `FileUploadService.check_file_upload_limit()`

#### Monthly File Upload Limits
- **Configuration**: `monthly_file_limit` field in `FileUploadSettings` model
- **Validation**: Checked in `FileUploadService.check_file_upload_limit()`

#### Per-Session File Upload Limits
- **Configuration**: `max_files_per_chat` field in `FileUploadSettings` model
- **Validation**: Checked in `FileUploadService.check_file_upload_limit()`

#### File Size Limits
- **Configuration**: `max_file_size` field in `FileUploadSettings` model
- **Validation**: Checked in `FileUploadService.check_file_size_limit()`

#### File Extension Restrictions
- **Configuration**: `allowed_extensions` field in `FileUploadSettings` model
- **Validation**: Checked in `FileUploadService.check_file_extension_allowed()`

### 6. Discount Code Usage Limits

Discount code applications are validated against usage restrictions:

#### Total Usage Limits
- **Configuration**: `max_uses` field in `DiscountCode` model
- **Validation**: Checked in `MessageValidationService.validate_discount_code_usage()`

#### Per-User Usage Limits
- **Configuration**: `max_uses_per_user` field in `DiscountCode` model
- **Validation**: Checked in `MessageValidationService.validate_discount_code_usage()`

#### Expiration Dates
- **Configuration**: `expires_at` field in `DiscountCode` model
- **Validation**: Checked in `MessageValidationService.validate_discount_code_usage()`

### 7. Subscription Upgrade Limits

Subscription changes are validated against eligibility requirements:

#### Active Subscription Requirement
- **Validation**: Checked in `MessageValidationService.validate_subscription_upgrade()`

#### Subscription Activation Status
- **Validation**: Checked in `MessageValidationService.validate_subscription_upgrade()`

## API Integration Points

### Chatbot App
- **ChatSessionViewSet.validate_message**: Pre-validation endpoint
- **ChatSessionViewSet.generate_title**: Title generation with validation
- **UploadedFileViewSet.create**: File upload with validation
- **UploadedImageViewSet.analyze**: Image analysis with validation
- **UploadedImageViewSet.upload_and_analyze**: Combined upload and analysis with validation
- **ChatMessageViewSet.regenerate**: Message regeneration with validation
- **ChatMessageViewSet.edit**: Message editing with validation

### Accounts App
- **UserViewSet.update_profile**: Profile updates with authentication validation
- **UserViewSet.change_password**: Password changes with authentication validation

### Subscriptions App
- **DiscountCodeViewSet.apply**: Discount application with usage validation
- **SubscriptionManagementViewSet.intelligent_upgrade**: Subscription upgrades with eligibility validation

### Message Processing
- **send_message view**: Comprehensive validation before AI interaction

## Validation Flow

1. **Pre-Validation**: All API endpoints check user authentication and basic permissions
2. **Resource Validation**: Specific resource limits are checked based on operation type
3. **Subscription Validation**: User's subscription type determines applicable limits
4. **Model Access Validation**: User's access to AI models is verified
5. **Usage Tracking**: Current usage is compared against configured limits
6. **Error Response**: Appropriate HTTP status codes and Persian error messages are returned

## Error Handling

### HTTP Status Codes
- **403 Forbidden**: Access restrictions (subscription required, model access denied)
- **429 Too Many Requests**: Rate limits (message count, token consumption, image generation)
- **500 Internal Server Error**: System errors

### Error Messages
All error messages are provided in Persian to match the user interface language requirements.

## Admin Configuration

All limitations can be configured through the Django admin interface:

1. **Subscription Types**: Configure message, token, image, and cost limits
2. **File Upload Settings**: Configure file upload restrictions per subscription
3. **Discount Codes**: Configure usage limits and expiration dates
4. **Limitation Messages**: Customize error messages for different limit types

## Testing

The validation system has been tested with:
- Unit tests for individual validation functions
- Integration tests for API endpoints
- End-to-end tests for message processing flow
- Limit boundary testing for edge cases

## Future Enhancements

1. Real-time usage tracking and notifications
2. Advanced fraud detection for abusive usage patterns
3. Concurrent session limits
4. Geographic-based restrictions
5. Dynamic limit adjustment based on usage patterns