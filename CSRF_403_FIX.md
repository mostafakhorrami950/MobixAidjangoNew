# Fix for 403 CSRF Error on Verify OTP Page

## Problem
After entering the verification code on the verify OTP page, users encountered a 403 Forbidden error.

## Root Cause
The issue was caused by CSRF (Cross-Site Request Forgery) protection misconfiguration:
1. Missing CSRF_TRUSTED_ORIGINS in Django 4.x
2. Insufficient CSRF cookie settings
3. Lack of proper error logging for CSRF failures

## Solution Applied

### 1. Updated `mobixai/settings.py`

#### Added CSRF_TRUSTED_ORIGINS
```python
# CSRF Trusted Origins (required for Django 4.0+)
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
if not CSRF_TRUSTED_ORIGINS and ALLOWED_HOSTS:
    # Auto-generate from ALLOWED_HOSTS if not explicitly set
    CSRF_TRUSTED_ORIGINS = [
        f"http://{host}" for host in ALLOWED_HOSTS if host and host != "*"
    ]
    CSRF_TRUSTED_ORIGINS += [
        f"https://{host}" for host in ALLOWED_HOSTS if host and host != "*"
    ]
```

#### Enhanced CSRF Settings
```python
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access
CSRF_COOKIE_SAMESITE = "Lax"  # Allow same-site requests
CSRF_USE_SESSIONS = False  # Use cookie-based tokens
CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"

# Don't require HTTPS for CSRF in development
if DEBUG:
    CSRF_COOKIE_SECURE = False
```

### 2. Enhanced `accounts/views.py`

Added comprehensive logging and error handling:
- Log all verify_otp requests
- Check for CSRF token presence
- Better error messages
- Exception handling for unexpected errors

## Configuration Required

### .env File
Add to your `.env` file:

```env
# For local development
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# For production (example)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Testing Steps

### 1. Update .env File
```bash
# Add this line to your .env
echo "CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000" >> .env
```

### 2. Clear Browser Data
- Clear cookies and cache
- Or use incognito/private mode

### 3. Test the Flow
1. Go to Register or Login page
2. Enter phone number
3. Receive OTP code
4. Enter OTP code on verify page
5. Click "تأیید کد" (Verify Code)
6. Should redirect to chat page successfully

### 4. Check Logs
If issues persist, check `django.log` for:
```
verify_otp called - Method: POST...
CSRF token present in POST request
Verifying OTP for user: 09...
```

## Verification

Run this command to verify the fix:
```bash
python manage.py shell
```

Then:
```python
from django.conf import settings
print("CSRF_TRUSTED_ORIGINS:", settings.CSRF_TRUSTED_ORIGINS)
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
print("DEBUG:", settings.DEBUG)
print("CSRF_COOKIE_SECURE:", settings.CSRF_COOKIE_SECURE)
```

## Common Issues & Solutions

### Issue 1: Still getting 403
**Solution:** Make sure your domain is in CSRF_TRUSTED_ORIGINS
```env
# Must include the protocol (http:// or https://)
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

### Issue 2: Works locally but not in production
**Solution:** Add your production domain to CSRF_TRUSTED_ORIGINS
```env
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Issue 3: CSRF token missing
**Solution:** The template already has `{% csrf_token %}`. Make sure:
1. You're not caching the page
2. Cookies are enabled in browser
3. Clear browser cache

## Files Modified

1. ✅ `mobixai/settings.py` - Added CSRF configuration
2. ✅ `accounts/views.py` - Added logging and error handling
3. ✅ Template already has `{% csrf_token %}` - No changes needed

## Status

✅ FIXED - Ready to test

## Next Steps

1. Update your `.env` file with CSRF_TRUSTED_ORIGINS
2. Restart Django server
3. Clear browser cache
4. Test the verify OTP flow

