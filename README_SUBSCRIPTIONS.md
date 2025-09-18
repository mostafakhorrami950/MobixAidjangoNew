# Subscription System Management

This document explains how to manage the subscription system and its automated tasks.

## Automated Tasks

The subscription system includes several automated tasks that should be run regularly:

### 1. Monthly Free Model Usage Reset

This task resets the monthly free model usage limits for all users on the first day of each month.

**Command:** `python manage.py reset_monthly_usage`

**Recommended Schedule:** Daily at midnight (will only run on the 1st of each month)

### 2. Expired Subscription Check

This task checks for expired subscriptions and deactivates them, resetting usage counters.

**Command:** `python manage.py check_expired_subscriptions`

**Recommended Schedule:** Daily at 1:00 AM

### 3. Subscription Renewals

This task handles automatic subscription renewals (if enabled).

**Command:** `python manage.py handle_subscription_renewals`

**Recommended Schedule:** Daily at 2:00 AM

## Setting up Cron Jobs (Linux/Unix)

Add the following lines to your crontab (`crontab -e`):

```bash
# Reset monthly free model usage (runs daily, but only acts on 1st of month)
0 0 * * * cd /path/to/your/project && /path/to/venv/bin/python manage.py reset_monthly_usage >> /var/log/subscription_reset.log 2>&1

# Check for expired subscriptions
0 1 * * * cd /path/to/your/project && /path/to/venv/bin/python manage.py check_expired_subscriptions >> /var/log/subscription_expired.log 2>&1

# Handle subscription renewals
0 2 * * * cd /path/to/your/project && /path/to/venv/bin/python manage.py handle_subscription_renewals >> /var/log/subscription_renewals.log 2>&1
```

## Setting up Task Scheduler (Windows)

For Windows servers, use Task Scheduler to create tasks with the following settings:

1. **Monthly Usage Reset:**
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `manage.py reset_monthly_usage`
   - Start in: `C:\path\to\your\project`
   - Schedule: Daily at midnight

2. **Expired Subscription Check:**
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `manage.py check_expired_subscriptions`
   - Start in: `C:\path\to\your\project`
   - Schedule: Daily at 1:00 AM

3. **Subscription Renewals:**
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `manage.py handle_subscription_renewals`
   - Start in: `C:\path\to\your\project`
   - Schedule: Daily at 2:00 AM

## Manual Execution

You can manually run any of these commands at any time:

```bash
# Reset monthly usage
python manage.py reset_monthly_usage

# Check expired subscriptions
python manage.py check_expired_subscriptions

# Handle renewals
python manage.py handle_subscription_renewals
```

## Token Usage Calculation Logic

The system implements professional subscription logic with the following rules:

1. **Token Counting:**
   - Each token represents one unit of usage from the AI model
   - Tokens are counted separately for input (prompt) and output (completion)
   - Free model tokens are tracked separately from paid model tokens

2. **Usage Periods:**
   - Usage is tracked in multiple time periods (hourly, daily, weekly, monthly)
   - Only the most relevant period is updated to avoid duplication
   - Free model usage is always tracked in monthly periods

3. **Reset Logic:**
   - Token counts are reset when:
     - A subscription is upgraded
     - A subscription is renewed
     - A subscription expires
     - Monthly free model limits are reset (1st of each month)

4. **Billing Cycle:**
   - Usage is calculated based on the user's current billing cycle
   - For users without active subscriptions, usage is tracked from the beginning of the current month
   - Expired subscriptions automatically reset usage counters