#!/bin/bash

echo "========================================="
echo "CSRF 403 Error Fix - Setup Script"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file first."
    exit 1
fi

echo "✓ .env file found"
echo ""

# Check if CSRF_TRUSTED_ORIGINS already exists
if grep -q "CSRF_TRUSTED_ORIGINS" .env; then
    echo "ℹ CSRF_TRUSTED_ORIGINS already exists in .env"
    echo "Current value:"
    grep "CSRF_TRUSTED_ORIGINS" .env
    echo ""
    read -p "Do you want to update it? (y/n): " update
    if [ "$update" != "y" ]; then
        echo "Skipping CSRF_TRUSTED_ORIGINS update"
    else
        # Remove old entry
        sed -i '/CSRF_TRUSTED_ORIGINS/d' .env
        # Add new entry
        echo "CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000" >> .env
        echo "✓ Updated CSRF_TRUSTED_ORIGINS"
    fi
else
    # Add CSRF_TRUSTED_ORIGINS
    echo "" >> .env
    echo "# CSRF Configuration" >> .env
    echo "CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000" >> .env
    echo "✓ Added CSRF_TRUSTED_ORIGINS to .env"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Restart your Django server"
echo "2. Clear your browser cache (Ctrl+Shift+Delete)"
echo "3. Test the verify OTP flow"
echo ""
echo "If you're running in production, update CSRF_TRUSTED_ORIGINS"
echo "to include your actual domain:"
echo "CSRF_TRUSTED_ORIGINS=https://yourdomain.com"
echo ""
