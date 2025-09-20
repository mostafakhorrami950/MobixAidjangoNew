# Free Model Token Limits Implementation

## Overview

This document describes the implementation of enhanced free model token limits and time-based restrictions for AI model usage. The system now provides more granular control over free token usage with comprehensive checking before sending messages to free models.

## Changes Made

### 1. Enhanced UsageService.comprehensive_check Method

The `comprehensive_check` method in [subscriptions/services.py](file:///c%3A/Users/10/Desktop/cursor/MobixAidjangoNew/subscriptions/services.py) has been enhanced to:

1. **Check max_tokens_free limit**: Before sending messages to free models, the system now checks if the user has exceeded their maximum allowed free tokens as defined in the subscription type.

2. **Implement time-based restrictions**: Added comprehensive time-based limit checking for free models:
   - Hourly limits
   - 3-hour limits
   - 12-hour limits
   - Daily limits
   - Weekly limits
   - Monthly limits

3. **Check message limits for free models**: Added checking for monthly message limits specific to free models

### 2. Implementation Details

#### Max Tokens Free Check
- The system retrieves the total free tokens used by calling `UsageService.get_user_total_tokens_from_chat_sessions(user, subscription_type)[1]`
- It compares this value against `subscription_type.max_tokens_free`
- If the limit is exceeded, it returns an appropriate Persian error message

#### Time-Based Restrictions
For each time period, the system:
1. Calculates the appropriate time range
2. Retrieves usage data specifically for free models using `UsageService.get_user_free_model_usage_for_period`
3. Checks if the token usage exceeds the configured limits
4. Returns specific error messages when limits are exceeded

#### Message Limits for Free Models
The system also checks:
1. Monthly message limits for free models using `subscription_type.monthly_free_model_messages`
2. Monthly token limits for free models using `subscription_type.monthly_free_model_tokens`

## Key Features

### Error Handling
The system provides clear, user-friendly error messages in Persian:
- "شما به حد مجاز توکن‌های رایگان ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز توکن‌های ساعتی ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز توکن‌های ۳ ساعتی ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز توکن‌های ۱۲ ساعتی ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز توکن‌های روزانه ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز توکن‌های هفتگی ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز توکن‌های ماهانه ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز پیام‌های مدل رایگان ماهانه ({limit} عدد) رسیده‌اید"
- "شما به حد مجاز توکن‌های مدل رایگان ماهانه ({limit} عدد) رسیده‌اید"

### Testing
A test script was created to verify the implementation:
- Tests the max_tokens_free limit checking
- Verifies time-based restriction enforcement
- Confirms message limit checking for free models
- Confirms appropriate error messages are returned

## Files Modified

1. [subscriptions/services.py](file:///c%3A/Users/10/Desktop/cursor/MobixAidjangoNew/subscriptions/services.py) - Enhanced the `comprehensive_check` method
2. [test_free_tokens_implementation.py](file:///c%3A/Users/10/Desktop/cursor/MobixAidjangoNew/test_free_tokens_implementation.py) - Created test script to verify functionality

## Database Schema

The implementation leverages existing database fields:
- `SubscriptionType.max_tokens_free` - Maximum free tokens allowed for a subscription
- Time-based limit fields in SubscriptionType:
  - `hourly_max_tokens`
  - `three_hours_max_tokens`
  - `twelve_hours_max_tokens`
  - `daily_max_tokens`
  - `weekly_max_tokens`
  - `monthly_max_tokens`
- Free model specific fields:
  - `monthly_free_model_messages`
  - `monthly_free_model_tokens`

## Usage Flow

1. When a user sends a message to an AI model:
   - The system first checks if the model is free (`ai_model.is_free`)
   - If it's a free model, it performs comprehensive limit checking
   - Checks max_tokens_free limit
   - Checks all time-based restrictions for free models
   - Checks message limits for free models
   - Only allows the request if all checks pass

2. If any limit is exceeded:
   - The request is denied
   - An appropriate error message is returned to the user

## Benefits

1. **Granular Control**: Administrators can now set precise limits on free model usage
2. **Fair Usage**: Prevents abuse of free resources while maintaining accessibility
3. **Clear Communication**: Users receive specific error messages explaining limit violations
4. **Flexible Configuration**: All limits can be configured per subscription type
5. **Comprehensive Coverage**: Covers all major time periods for fine-grained control
6. **Message Limit Control**: Separate control over message count and token usage for free models