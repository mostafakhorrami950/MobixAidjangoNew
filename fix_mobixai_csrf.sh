#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║  CSRF 403 Fix for mobixai.ir Production               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Make sure you're in the project root directory."
    exit 1
fi

echo "✓ Found .env file"
echo ""

# Create backup
BACKUP_FILE=".env.backup.$(date +%Y%m%d_%H%M%S)"
cp .env "$BACKUP_FILE"
echo "✓ Created backup: $BACKUP_FILE"
echo ""

# Check if CSRF_TRUSTED_ORIGINS exists
if grep -q "^CSRF_TRUSTED_ORIGINS=" .env; then
    echo "⚠ CSRF_TRUSTED_ORIGINS already exists:"
    grep "^CSRF_TRUSTED_ORIGINS=" .env
    echo ""
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old entry
        sed -i.tmp '/^CSRF_TRUSTED_ORIGINS=/d' .env
        # Add new entry
        echo "" >> .env
        echo "# CSRF Configuration for mobixai.ir" >> .env
        echo "CSRF_TRUSTED_ORIGINS=https://mobixai.ir,https://www.mobixai.ir" >> .env
        rm -f .env.tmp
        echo "✓ Updated CSRF_TRUSTED_ORIGINS"
    else
        echo "Skipped update"
    fi
else
    # Add CSRF_TRUSTED_ORIGINS
    echo "" >> .env
    echo "# CSRF Configuration for mobixai.ir" >> .env
    echo "CSRF_TRUSTED_ORIGINS=https://mobixai.ir,https://www.mobixai.ir" >> .env
    echo "✓ Added CSRF_TRUSTED_ORIGINS to .env"
fi

echo ""
echo "Current configuration:"
grep "CSRF_TRUSTED_ORIGINS=" .env
echo ""

# Detect and restart service
echo "Detecting service type..."
echo ""

if systemctl list-units --type=service | grep -q gunicorn; then
    echo "Detected: Gunicorn with systemd"
    read -p "Restart gunicorn service? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl restart gunicorn
        echo "✓ Gunicorn restarted"
    fi
elif command -v supervisorctl &> /dev/null; then
    echo "Detected: Supervisor"
    read -p "Restart mobixai service? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo supervisorctl restart mobixai
        echo "✓ Service restarted"
    fi
elif [ -f "docker-compose.yml" ]; then
    echo "Detected: Docker Compose"
    read -p "Restart docker containers? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose restart
        echo "✓ Containers restarted"
    fi
else
    echo "⚠ Could not detect service type"
    echo "Please restart your Django application manually"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Configuration Complete!                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "✅ What was done:"
echo "   • Backed up .env to $BACKUP_FILE"
echo "   • Added/Updated CSRF_TRUSTED_ORIGINS"
echo "   • Service restart initiated"
echo ""
echo "🧪 Next steps:"
echo "   1. Clear your browser cache (Ctrl+Shift+Delete)"
echo "   2. Go to https://mobixai.ir/accounts/login/"
echo "   3. Test the login and OTP verification"
echo ""
echo "🔍 Verify configuration:"
echo "   python manage.py shell"
echo "   >>> from django.conf import settings"
echo "   >>> print(settings.CSRF_TRUSTED_ORIGINS)"
echo ""
echo "📋 Check logs if issues persist:"
echo "   tail -f django.log"
echo ""

