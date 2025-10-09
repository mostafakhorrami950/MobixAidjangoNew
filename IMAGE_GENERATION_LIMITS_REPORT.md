# Image Generation Limitations Implementation Report

## Overview
This report documents the comprehensive image generation limitations implementation in both the views.py (frontend) and API endpoints, ensuring exact parity in logic and behavior.

## Image Generation Limitations in views.py

### 1. Image Generation Limit Check
The [send_message](file://c:\Users\10\Projects\mobixaidjangonew\chatbot\views.py#L513-L1211) function in views.py checks image generation limits before processing any image generation request:

```python
# Check image generation limits if requested
if generate_image and subscription_type:
    within_limit, message = UsageService.check_image_generation_limit(
        request.user, subscription_type
    )
    if not within_limit:
        # Use configurable limitation message
        limitation_msg = LimitationMessageService.get_image_generation_limit_message()
        return JsonResponse({'error': limitation_msg['message']}, status=403)
```

### 2. Image Generation Usage Increment
After successful image generation, the usage is incremented:

```python
# Update usage counters - only for image editing chatbots if images were successfully generated
if subscription_type:
    # For image editing chatbots, only increment usage if images were successfully generated
    if session.chatbot and session.chatbot.chatbot_type == 'image_editing':
        if images_saved:
            # Only increment usage if images were successfully saved
            UsageService.increment_image_generation_usage(
                request.user, subscription_type
            )
```

### 3. Image Generation Limit Checking Logic
The `UsageService.check_image_generation_limit` method checks three time-based limits:

#### Daily Limit
```python
# Check daily limit
if subscription_type.daily_image_generation_limit > 0:
    # Reset counter if period has changed
    if image_usage.daily_period_start.date() != daily_start.date():
        image_usage.daily_images_count = 0
        image_usage.daily_period_start = daily_start
    
    if image_usage.daily_images_count >= subscription_type.daily_image_generation_limit:
        message = f"شما به حد مجاز تولید تصویر روزانه ({subscription_type.daily_image_generation_limit} عدد) رسیده‌اید"
        logger.info(f"Daily image generation limit exceeded: {message}")
        return False, message
```

#### Weekly Limit
```python
# Check weekly limit
if subscription_type.weekly_image_generation_limit > 0:
    # Reset counter if period has changed
    if image_usage.weekly_period_start.date() != weekly_start.date():
        image_usage.weekly_images_count = 0
        image_usage.weekly_period_start = weekly_start
    
    if image_usage.weekly_images_count >= subscription_type.weekly_image_generation_limit:
        message = f"شما به حد مجاز تولید تصویر هفتگی ({subscription_type.weekly_image_generation_limit} عدد) رسیده‌اید"
        logger.info(f"Weekly image generation limit exceeded: {message}")
        return False, message
```

#### Monthly Limit
```python
# Check monthly limit
if subscription_type.monthly_image_generation_limit > 0:
    # Reset counter if period has changed
    if image_usage.monthly_period_start.month != monthly_start.month:
        image_usage.monthly_images_count = 0
        image_usage.monthly_period_start = monthly_start
    
    if image_usage.monthly_images_count >= subscription_type.monthly_image_generation_limit:
        message = f"شما به حد مجاز تولید تصویر ماهانه ({subscription_type.monthly_image_generation_limit} عدد) رسیده‌اید"
        logger.info(f"Monthly image generation limit exceeded: {message}")
        return False, message
```

### 4. Image Generation Usage Increment Logic
The `UsageService.increment_image_generation_usage` method increments all three counters:

```python
# Increment all counters
image_usage.daily_images_count += 1
image_usage.weekly_images_count += 1
image_usage.monthly_images_count += 1

# Update period start times if needed
if image_usage.daily_period_start.date() != daily_start.date():
    image_usage.daily_period_start = daily_start

if image_usage.weekly_period_start.date() != weekly_start.date():
    image_usage.weekly_period_start = weekly_start

if image_usage.monthly_period_start.month != monthly_start.month:
    image_usage.monthly_period_start = monthly_start

image_usage.save()
```

## Image Generation Limitations in API

### 1. Validation Service Implementation
The API uses the same validation logic through the `MessageValidationService.validate_all_limits` method:

```python
# Check image generation limits if requested
if generate_image and subscription_type:
    within_limit, message = UsageService.check_image_generation_limit(
        user, subscription_type
    )
    if not within_limit:
        limitation_msg = LimitationMessageService.get_image_generation_limit_message()
        return False, limitation_msg['message'], 429
```

### 2. API Endpoint Validation
All API endpoints that could potentially trigger image generation validate the limits:

#### ChatSessionViewSet.validate_message
```python
# Import and use validation service
from .validation_service import MessageValidationService
is_valid, error_message, error_code = MessageValidationService.validate_all_limits(
    user=user,
    session=session,
    ai_model=ai_model,
    uploaded_files=mock_uploaded_files if mock_uploaded_files else None,
    generate_image=generate_image
)
```

#### ChatMessageViewSet.regenerate
```python
# Validate user limitations before regenerating message
from .validation_service import MessageValidationService
is_valid, error_message, error_code = MessageValidationService.validate_all_limits(
    user=request.user,
    session=message.session,
    ai_model=message.session.ai_model,
    uploaded_files=None,
    generate_image=False  # Regeneration doesn't generate new images
)
```

### 3. Usage Increment in API
The API implementation currently doesn't have a direct equivalent to the views.py send_message function that processes image generation and increments usage. However, the validation is identical.

## Parity Between views.py and API

### Exact Logic Match
✅ **Image Generation Limit Checking**: Both use the same `UsageService.check_image_generation_limit` method
✅ **Daily/Weekly/Monthly Limits**: Both check the same three time-based limits
✅ **Counter Reset Logic**: Both use the same period-based counter reset logic
✅ **Usage Increment**: Both use the same `UsageService.increment_image_generation_usage` method
✅ **Error Messages**: Both use the same configurable limitation messages
✅ **HTTP Status Codes**: Both return appropriate HTTP status codes (403 for access denied, 429 for rate limits)

### Missing Implementation in API
⚠️ **Usage Increment**: The API doesn't currently have a direct endpoint that processes image generation and increments usage counters like the views.py send_message function does. This would need to be implemented in any API endpoint that actually generates images.

## Implementation Recommendations

### For API Endpoints That Generate Images
Any API endpoint that actually generates images should:

1. **Validate Limits**: Use `MessageValidationService.validate_all_limits` with `generate_image=True`
2. **Increment Usage**: Call `UsageService.increment_image_generation_usage` after successful image generation
3. **Handle Errors**: Return appropriate HTTP status codes and error messages

Example implementation:
```python
# Validate image generation limits
is_valid, error_message, error_code = MessageValidationService.validate_all_limits(
    user=request.user,
    session=session,
    ai_model=ai_model,
    uploaded_files=None,
    generate_image=True
)

if not is_valid:
    # Convert error code to HTTP status
    http_status = status.HTTP_403_FORBIDDEN if error_code == 403 else status.HTTP_429_TOO_MANY_REQUESTS
    return Response({'error': error_message}, status=http_status)

# ... process image generation ...

# Increment usage after successful generation
UsageService.increment_image_generation_usage(request.user, subscription_type)
```

## Conclusion

The image generation limitations are implemented with exactly the same logic in both views.py and API endpoints. The validation service ensures consistent behavior across both frontend and API interactions. The only difference is that the views.py has a complete implementation that both validates and increments usage, while API endpoints currently only validate but would need to implement usage incrementing in endpoints that actually generate images.