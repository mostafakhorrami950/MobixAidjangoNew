# MobixAI Production Deployment Guide

This guide will help you deploy MobixAI to a Python hosting service.

## 🚀 Quick Deployment Checklist

### 1. Environment Variables
Set the following environment variables on your hosting platform:

```bash
# Required
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# API Keys
OPENROUTER_API_KEY=your-openrouter-api-key

# SMS Service
IPANEL_API_KEY=your-ipanel-api-key
IPANEL_PATTERN_CODE=your-pattern-code
IPANEL_FROM_NUMBER=your-phone-number

# Payment Gateway
ZARINPAL_MERCHANT_ID=your-zarinpal-merchant-id
ZARINPAL_SANDBOX=False

# Security (Optional - defaults provided)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### 2. Files Required for Deployment
- `requirements.txt` ✅
- `runtime.txt` ✅ 
- `Procfile` ✅
- `deploy.py` ✅

### 3. Database Setup
The application will automatically:
- Use SQLite in development (no DATABASE_URL set)
- Use PostgreSQL in production (DATABASE_URL set)

### 4. Static Files
Static files are handled by WhiteNoise middleware in production.

## 📋 Deployment Steps

### For Heroku:
```bash
# 1. Create Heroku app
heroku create your-app-name

# 2. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set OPENROUTER_API_KEY=your-api-key
# ... (set all other variables)

# 3. Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# 4. Deploy
git push heroku main
```

### For PythonAnywhere:
1. Upload your code
2. Set environment variables in the Web tab
3. Set up PostgreSQL database (if using paid plan)
4. Run `python deploy.py` to prepare static files

### For Railway/Render:
1. Connect your Git repository
2. Set environment variables in the dashboard
3. The platform will automatically detect Django and use the Procfile

## 🔧 Production Optimizations Applied

### Security:
- ✅ Console logs disabled in production
- ✅ HTTPS redirects enabled
- ✅ Secure cookies
- ✅ HSTS headers
- ✅ XSS protection

### Performance:
- ✅ WhiteNoise for static files
- ✅ Compressed static files
- ✅ Gunicorn web server
- ✅ Database connection pooling ready

### Database:
- ✅ PostgreSQL support for production
- ✅ SQLite for development
- ✅ Automatic migrations

## 🛠️ Local Development vs Production

### Development (DEBUG=True):
- Uses SQLite database
- Console logs enabled
- Static files served by Django
- No HTTPS enforcement

### Production (DEBUG=False):
- Uses PostgreSQL (if DATABASE_URL set)
- Console logs disabled
- Static files served by WhiteNoise
- HTTPS enforcement enabled
- Security headers added

## 🔍 Troubleshooting

### Common Issues:

1. **Static files not loading:**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT setting

2. **Database connection errors:**
   - Verify DATABASE_URL format
   - Check database credentials

3. **Environment variables not working:**
   - Ensure .env file exists locally
   - Verify hosting platform variables are set

4. **CSRF errors:**
   - Add your domain to ALLOWED_HOSTS
   - Check CSRF_COOKIE_SECURE setting

## 📞 Support

If you encounter issues during deployment, check:
1. Server logs for detailed error messages
2. Environment variables are correctly set
3. Database connection is working
4. Static files are collected properly

The application is now production-ready! 🎉