# Comprehensive Usage Limit Checking Implementation

## Overview

This document describes the implementation of comprehensive usage limit checking before sending any message to the AI. The system now performs all required validations before allowing AI interaction.

## Implementation Details

### 1. UsageService.comprehensive_check Method

The `UsageService.comprehensive_check` method in `subscriptions/services.py` performs all required validations:

1. **Model Access Check**: Verifies if the user has access to the selected AI model
2. **Free Model Limits**: Checks if free model token limits are exceeded
3. **Time-based Usage Limits**: Checks all time periods (hourly, 3-hour, 12-hour, daily, weekly, monthly)
4. **Subscription Token Limits**: Checks if the user has exceeded their subscription's max token limit

### 2. Integration with send_message View

The `send_message` view in `chatbot/views.py` now calls the comprehensive check before processing any AI request:

```python
# Perform comprehensive usage limit checking before sending any message to AI
if subscription_type:
    # Check all usage limits comprehensively
    within_limit, message = UsageService.comprehensive_check(
        request.user, ai_model, subscription_type
    )
    if not within_limit:
        return JsonResponse({'error': message}, status=403)
```

### 3. Error Messages

The system returns specific Persian error messages for each type of limit violation:
- "دسترسی به این مدل دیگر برای اشتراک شما فعال نیست" (Model access denied)
- "توکن رایگان شما برای مدل رایگان تمام شده است" (Free model tokens exhausted)
- "شما به حد مجاز پیام‌های [time_period] ([limit] عدد) رسیده‌اید" (Message limit exceeded)
- "شما به حد مجاز توکن‌های [time_period] ([limit] عدد) رسیده‌اید" (Token limit exceeded)
- "بودجه باقیمانده‌ی توکن شما برای این مدل کافی نیست ([remaining] عدد)" (Insufficient token budget)

## Testing

The implementation has been tested and verified to work correctly:
- Users with exceeded limits are properly blocked
- Users with valid access are allowed to proceed
- Free models are handled correctly
- All time-based limits are properly enforced

## Benefits

1. **Comprehensive Protection**: All usage limits are checked before any AI interaction
2. **Clear Error Messages**: Users receive specific feedback about why their request was denied
3. **Performance**: All checks are performed efficiently without unnecessary database queries
4. **Maintainability**: The logic is centralized in one method for easy updates