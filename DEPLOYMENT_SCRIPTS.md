# Deployment Scripts

This document explains how to use the automated deployment scripts for populating initial data in the MobixAI application.

## Available Scripts

### 1. populate_all_data_fixed.py
A standalone Python script that populates all initial data including:
- AI Models
- Chatbots
- Subscription Types
- Limitation Messages
- Sidebar Menu Items
- Global Settings
- Default Chat Settings
- Terms and Conditions

**Usage:**
```bash
cd c:\Users\10\Projects\mobixaidjangonew
python populate_all_data_fixed.py
```

### 2. Django Management Command
A Django management command that does the same as the standalone script.

**Usage:**
```bash
cd c:\Users\10\Projects\mobixaidjangonew
python manage.py populate_all_data
```

### 3. Reset All Data Command
A Django management command that deletes all existing data and repopulates with initial data.

**Usage:**
```bash
cd c:\Users\10\Projects\mobixaidjangonew
python manage.py reset_all_data [--no-input]
```

Use the `--no-input` flag to skip the confirmation prompt. **Warning:** This command will permanently delete all existing data!

## What Data Gets Populated

### AI Models
- GPT-4 Turbo (text generation)
- Claude 3 Opus (text generation)
- Gemini Pro (text generation, free model)
- DALL-E 3 (image generation)
- Stable Diffusion XL (image generation)

### Subscription Types
- Free: Limited access with usage restrictions
- Premium: Full access with higher limits

### Chatbots
- General Assistant
- Creative Writer
- Technical Expert
- Image Generator

### Limitation Messages
Persian language messages for various limitation types:
- Token limits
- Message limits
- Daily/weekly/monthly limits
- File upload limits
- Image generation limits
- Subscription requirements
- Model access restrictions

### Sidebar Menu Items
- چت جدید (New Chat)
- تاریخچه چت (Chat History)
- مدل‌های هوش مصنوعی (AI Models)
- اشتراک من (My Subscription)
- خرید اشتراک (Purchase Subscription)
- ورود / ثبت نام (Login/Register)
- هزینه‌های استفاده (Usage Costs)

### Global Settings
Default application settings for file uploads, session timeouts, and API rate limits.

### Terms and Conditions
Default terms and conditions content.

### Default Chat Settings
Sets Gemini Pro as the default AI model and General Assistant as the default chatbot.

## Running the Scripts

### For New Deployments
1. Make sure your Django application is properly configured
2. Run database migrations: `python manage.py migrate`
3. Run the population script: `python manage.py populate_all_data` or `python populate_all_data_fixed.py`

### For Updates
The scripts are safe to run multiple times - they will create missing data and update existing data as needed.

## Troubleshooting

If you encounter any issues:
1. Make sure all database migrations have been applied
2. Check that your database is accessible
3. Ensure all required environment variables are set
4. Verify that Django is properly configured

The scripts will show detailed output about what data is being created or updated.