# New Usage Structure Implementation

## Overview

This document describes the implementation of a new usage tracking structure that creates individual records for each usage event instead of aggregating data by time periods. This approach provides more accurate and flexible usage tracking.

## Changes Made

### 1. Database Schema Changes

Modified the `UserUsage` model in `subscriptions/models.py`:
- Removed `period_start` and `period_end` fields
- Removed the `unique_together` constraint on `('user', 'subscription_type', 'period_start')`
- Kept `created_at` field for time-based filtering

### 2. Admin Panel Updates

Updated the `UserUsageAdmin` class in `subscriptions/admin.py`:
- Removed `period_start` and `period_end` from `list_display`
- Removed `period_start` and `period_end` from `list_filter`

### 3. Service Layer Enhancements

Updated the `UsageService` class in `subscriptions/services.py`:

#### increment_usage Method
- Now creates a new record for each usage event instead of updating existing records
- Simplified logic that no longer needs to determine time periods
- Properly handles free model vs. premium model usage

#### get_user_usage_for_period Method
- Now filters records based on `created_at` field instead of `period_start`/`period_end`
- Uses Django's `Sum` aggregation for efficient calculation
- Properly combines regular and free model token counts

#### get_user_free_model_usage_for_period Method
- Now filters records based on `created_at` field
- Uses Django's `Sum` aggregation for efficient calculation
- Specifically tracks free model usage

## Implementation Details

### Individual Record Creation

Instead of aggregating usage data into daily/period records, each usage event now creates a separate record:
- Each message sent to AI creates a new `UserUsage` record
- Records contain exact message and token counts for that specific event
- Timestamps are automatically captured with `created_at`

### Time-Based Filtering

Usage calculations now use the `created_at` field for time-based filtering:
- Hourly usage: Records created in the last hour
- Daily usage: Records created today
- Weekly usage: Records created in the current week
- Monthly usage: Records created in the current month

### Benefits

1. **Accuracy**: Each usage event is tracked individually with precise timestamps
2. **Flexibility**: Can calculate usage for any time period, not just predefined periods
3. **Simplicity**: Removed complex period calculation logic
4. **Performance**: Efficient database queries using Django's aggregation functions
5. **Scalability**: Better suited for high-volume usage tracking

## Testing

The implementation has been tested and verified to work correctly:
- New usage records are properly created for each event
- Time-based filtering works correctly using the `created_at` field
- Aggregation functions properly calculate total usage
- Free model usage is tracked separately
- Admin panel displays correctly without errors

## Migration

The database migration:
1. Removes the `period_start` and `period_end` fields from `UserUsage` table
2. Removes the unique constraint on `('user', 'subscription_type', 'period_start')`
3. Preserves all existing data in the table

## Backward Compatibility

The changes maintain backward compatibility with existing code:
- Method signatures remain the same
- Return values are unchanged
- Existing usage data can still be queried (though period fields are now null)