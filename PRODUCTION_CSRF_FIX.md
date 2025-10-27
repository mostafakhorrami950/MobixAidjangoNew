# Production 403 Error Fix for mobixai.ir

## Issue
Getting 403 Forbidden error on https://mobixai.ir/accounts/verify-otp/

## Solution

### Step 1: Update Production .env File

Add this line to your production `.env` file:

```env
CSRF_TRUSTED_ORIGINS=https://mobixai.ir,https://www.mobixai.ir
```

**IMPORTANT:** 
- Must use `https://` (not `http://`)
- Must include both with and without `www`
- No trailing slashes

### Step 2: Apply the Fix

SSH into your production server and run:

```bash
# Navigate to project directory
cd /path/to/mobixaidjangonew

# Backup current .env
cp .env .env.backup

# Add CSRF_TRUSTED_ORIGINS (if not exists)
if ! grep -q "CSRF_TRUSTED_ORIGINS" .env; then
    echo "" >> .env
    echo "# CSRF Configuration for Production" >> .env
    echo "CSRF_TRUSTED_ORIGINS=https://mobixai.ir,https://www.mobixai.ir" >> .env
    echo "✓ Added CSRF_TRUSTED_ORIGINS"
else
    echo "CSRF_TRUSTED_ORIGINS already exists. Please update manually."
fi

# Restart your Django application
# Choose one based on your setup:

# If using gunicorn with systemd:
sudo systemctl restart gunicorn

# If using supervisor:
sudo supervisorctl restart mobixai

# If using docker:
docker-compose restart web

# If using screen/tmux (manual restart needed)
# Stop the current process and restart with:
# python manage.py runserver 0.0.0.0:8000
```

### Step 3: Verify the Configuration

```bash
# Check if the setting is in .env
grep CSRF_TRUSTED_ORIGINS .env

# Should show:
# CSRF_TRUSTED_ORIGINS=https://mobixai.ir,https://www.mobixai.ir
```

### Step 4: Test

1. Clear browser cache (Ctrl+Shift+Delete)
2. Go to https://mobixai.ir/accounts/login/
3. Enter phone number
4. Enter OTP code
5. Click submit
6. Should work now! ✅

## Alternative: Manual Update

If you prefer to edit manually:

```bash
# Edit .env file
nano .env

# Or
vim .env

# Add this line at the end:
CSRF_TRUSTED_ORIGINS=https://mobixai.ir,https://www.mobixai.ir

# Save and exit (Ctrl+X, Y, Enter for nano)

# Restart application
sudo systemctl restart gunicorn
```

## Verification Commands

```bash
# Check Django settings (in production)
python manage.py shell

# Then in shell:
from django.conf import settings
print("CSRF_TRUSTED_ORIGINS:", settings.CSRF_TRUSTED_ORIGINS)
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
print("CSRF_COOKIE_SECURE:", settings.CSRF_COOKIE_SECURE)

# Should show:
# CSRF_TRUSTED_ORIGINS: ['https://mobixai.ir', 'https://www.mobixai.ir']
# ALLOWED_HOSTS: [...your hosts...]
# CSRF_COOKIE_SECURE: True
```

## Check Logs

If still not working, check logs:

```bash
# Check Django logs
tail -f django.log

# Or application logs
tail -f /var/log/gunicorn/error.log

# Look for:
# "verify_otp called - Method: POST"
# "CSRF token present in POST request"
```

## Common Issues

### Issue 1: Still getting 403
**Cause:** Service not restarted  
**Solution:** Make sure to restart after updating .env

### Issue 2: Mixed content error
**Cause:** Using http instead of https  
**Solution:** Make sure .env has `https://` not `http://`

### Issue 3: Domain mismatch
**Cause:** Accessing via different domain  
**Solution:** Add all domains you use to CSRF_TRUSTED_ORIGINS

## Quick Fix Script

Save this as `fix_production_csrf.sh`:

```bash
#!/bin/bash
echo "Fixing CSRF for mobixai.ir..."

# Add CSRF_TRUSTED_ORIGINS if not exists
if ! grep -q "CSRF_TRUSTED_ORIGINS" .env; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "" >> .env
    echo "# CSRF Configuration" >> .env
    echo "CSRF_TRUSTED_ORIGINS=https://mobixai.ir,https://www.mobixai.ir" >> .env
    echo "✓ Added CSRF_TRUSTED_ORIGINS"
else
    echo "ℹ CSRF_TRUSTED_ORIGINS already exists"
    grep CSRF_TRUSTED_ORIGINS .env
fi

# Restart service (adjust based on your setup)
echo "Restarting service..."
sudo systemctl restart gunicorn || sudo supervisorctl restart mobixai || echo "Please restart manually"

echo "✓ Done! Test at https://mobixai.ir/accounts/verify-otp/"
```

Run with:
```bash
chmod +x fix_production_csrf.sh
./fix_production_csrf.sh
```

## Status Check

After applying the fix, verify:

- [ ] .env file has CSRF_TRUSTED_ORIGINS with https://mobixai.ir
- [ ] Django service restarted
- [ ] Browser cache cleared
- [ ] Test login flow works
- [ ] No 403 error on verify OTP page

