-- اسکریپت تغییر charset دیتابیس و جداول به utf8mb4 برای پشتیبانی کامل از فارسی
-- قبل از اجرا، نام دیتابیس خود را جایگزین YOUR_DATABASE_NAME کنید

-- تغییر charset کل دیتابیس
ALTER DATABASE YOUR_DATABASE_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- استفاده از دیتابیس
USE YOUR_DATABASE_NAME;

-- تولید دستورات تغییر charset برای تمام جداول
SELECT CONCAT('ALTER TABLE ', table_name, ' CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;') AS alter_statement
FROM information_schema.tables
WHERE table_schema = 'YOUR_DATABASE_NAME'
AND table_type = 'BASE TABLE';

-- جداول اصلی Django که معمولاً وجود دارند
ALTER TABLE django_migrations CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE django_content_type CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE auth_permission CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE django_session CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE django_admin_log CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- جداول پروژه (در صورت وجود)
-- جداول کاربران
ALTER TABLE accounts_user CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE accounts_user_groups CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE accounts_user_user_permissions CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- جداول OTP
ALTER TABLE otp_codes CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- جداول چت‌بات
ALTER TABLE chatbot_chatbot CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE chatbot_chatsession CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE chatbot_chatmessage CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE chatbot_uploadedfile CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE chatbot_chatsessionusage CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- جداول مدل‌های هوش مصنوعی
ALTER TABLE ai_models_aimodel CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE ai_models_modelsubscription CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE ai_models_modelsubscription_subscription_types CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- جداول اشتراک‌ها
ALTER TABLE subscriptions_subscriptiontype CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE subscriptions_usersubscription CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE subscriptions_financialtransaction CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE subscriptions_discountcode CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- بررسی charset جداول
SELECT 
    TABLE_NAME,
    TABLE_COLLATION,
    TABLE_SCHEMA
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'YOUR_DATABASE_NAME';

-- بررسی charset ستون‌ها
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CHARACTER_SET_NAME,
    COLLATION_NAME
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'YOUR_DATABASE_NAME' 
AND CHARACTER_SET_NAME IS NOT NULL;

-- تنظیمات پیش‌فرض برای connection
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- پیام تکمیل
SELECT 'Migration to utf8mb4 completed. Please verify all tables and restart your Django application.' AS status;