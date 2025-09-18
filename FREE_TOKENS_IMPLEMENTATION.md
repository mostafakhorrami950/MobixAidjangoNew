# Free Tokens Implementation

## Overview

This document describes the implementation of enhanced free token limits checking for AI model usage. The system now provides more granular control over free token usage with time-based limits.

## Changes Made

### 1. Database Schema Changes

Added a new field `max_tokens_free` to the `SubscriptionType` model:
- Field type: Integer
- Default value: 0 (unlimited)
- Purpose: Defines the maximum number of free tokens allowed for a subscription type

### 2. Admin Panel Updates

Updated the SubscriptionType admin panel to include the `max_tokens_free` field in the "Subscription Details" section.

### 3. Usage Service Enhancements

Enhanced the `UsageService.comprehensive_check` method to:
- Check max_tokens_free limit before sending messages to free models
- Properly check time-based limits for free models
- Enforce limits for all time periods (hourly, 3-hour, 12-hour, daily, weekly, monthly)
- Return appropriate Persian error messages when limits are exceeded

### 4. Chat View Improvements

Updated the `send_message` view to:
- Calculate actual token counts more accurately
- Pass accurate token information to the usage checking functions

## Implementation Details

### Max Tokens Free Check

For free models, the system now checks the total free tokens used against the `max_tokens_free` limit:
- Retrieves total free tokens used from chat sessions
- Compares against the subscription's `max_tokens_free` limit
- Denies access if the limit is exceeded

### Time-Based Limit Checking

For free models, the system now checks all time-based limits:
1. **Hourly Limits**: Checks tokens used in the last hour
2. **3-Hour Limits**: Checks tokens used in the last 3 hours
3. **12-Hour Limits**: Checks tokens used in the last 12 hours
4. **Daily Limits**: Checks tokens used in the current day
5. **Weekly Limits**: Checks tokens used in the current week
6. **Monthly Limits**: Checks tokens used in the current month

## Testing

The implementation has been tested and verified to work correctly:
- The new `max_tokens_free` field is properly added to the database
- The admin panel correctly displays and allows editing of the field
- Time-based limits are properly enforced for free models
- Max tokens free limit is properly checked
- Appropriate error messages are returned when limits are exceeded