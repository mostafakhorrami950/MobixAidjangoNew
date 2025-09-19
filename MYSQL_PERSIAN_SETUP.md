# راهنمای راه‌اندازی MySQL برای پشتیبانی از زبان فارسی

این راهنما مراحل کاملی برای پیکربندی دیتابیس MySQL جهت پشتیبانی کامل از متن‌های فارسی در پروژه Django ارائه می‌دهد.

## مرحله ۱: نصب MySQL و تنظیمات اولیه

### نصب MySQL (اختیاری اگر قبلاً نصب شده)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server

# macOS
brew install mysql

# Windows
# دانلود از: https://dev.mysql.com/downloads/mysql/
```

### پیکربندی اولیه MySQL

```bash
sudo mysql_secure_installation
```

## مرحله ۲: ایجاد دیتابیس با charset مناسب

```sql
-- ایجاد دیتابیس با charset فارسی
CREATE DATABASE mobixai_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- ایجاد کاربر دیتابیس
CREATE USER 'mobixai_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- اعطای دسترسی‌ها
GRANT ALL PRIVILEGES ON mobixai_db.* TO 'mobixai_user'@'localhost';
FLUSH PRIVILEGES;

-- تست اتصال
USE mobixai_db;
SELECT 'سلام دنیا! این یک تست فارسی است' AS test_persian;
```

## مرحله ۳: پیکربندی فایل تنظیمات MySQL

### ویرایش فایل `/etc/mysql/my.cnf` (Linux) یا `my.ini` (Windows)

```ini
[client]
default-character-set = utf8mb4

[mysql]
default-character-set = utf8mb4

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
init-connect = 'SET NAMES utf8mb4'

# پیکربندی برای بهینه‌سازی
innodb_file_format = Barracuda
innodb_file_per_table = 1
innodb_large_prefix = 1
```

### راه‌اندازی مجدد MySQL

```bash
# Linux
sudo systemctl restart mysql

# macOS
brew services restart mysql

# Windows
# از طریق Services Panel یا:
net stop mysql
net start mysql
```

## مرحله ۴: پیکربندی Django

### نصب درایور MySQL

```bash
pip install mysqlclient
```

### تنظیمات فایل .env

```env
# MySQL Database Configuration
MYSQL_DATABASE=mobixai_db
MYSQL_USER=mobixai_user
MYSQL_PASSWORD=your_secure_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

### تنظیمات settings.py (قبلاً انجام شده)

تنظیمات دیتابیس در فایل `settings.py` به‌روزرسانی شده است.

## مرحله ۵: اجرای اسکریپت مایگریشن

### اجرای فایل SQL برای تغییر charset

```bash
# ورود به MySQL
mysql -u mobixai_user -p mobixai_db

# اجرای اسکریپت مایگریشن
source mysql_utf8mb4_migration.sql
```

یا:

```bash
mysql -u mobixai_user -p mobixai_db < mysql_utf8mb4_migration.sql
```

**نکته مهم:** قبل از اجرا، در فایل `mysql_utf8mb4_migration.sql` عبارت `YOUR_DATABASE_NAME` را با `mobixai_db` جایگزین کنید.

## مرحله ۶: مایگریشن Django

```bash
# ایجاد مایگریشن‌های جدید
python manage.py makemigrations

# اجرای مایگریشن‌ها
python manage.py migrate

# ایجاد superuser (اختیاری)
python manage.py createsuperuser
```

## مرحله ۷: تست سیستم

### اجرای اسکریپت تست

```bash
python test_database_persian.py
```

### تست دستی

```bash
python manage.py shell
```

```python
from accounts.models import User

# ایجاد کاربر با متن فارسی
user = User.objects.create_user(
    phone_number="09123456789",
    name="علی احمدی - تست فارسی",
    username="test_user"
)

# بازیابی و نمایش
retrieved_user = User.objects.get(phone_number="09123456789")
print(retrieved_user.name)  # باید متن فارسی را صحیح نمایش دهد

# پاک کردن
retrieved_user.delete()
```

## مرحله ۸: تنظیمات Production

### متغیرهای محیطی Production

```env
MYSQL_DATABASE=mobixai_production
MYSQL_USER=mobixai_prod_user
MYSQL_PASSWORD=very_secure_production_password
MYSQL_HOST=your_production_db_host
MYSQL_PORT=3306
```

### Backup و Restore با حفظ charset

```bash
# Backup
mysqldump -u mobixai_user -p --default-character-set=utf8mb4 \
  --single-transaction mobixai_db > backup.sql

# Restore
mysql -u mobixai_user -p --default-character-set=utf8mb4 \
  mobixai_db < backup.sql
```

## عیب‌یابی مشکلات رایج

### مشکل ۱: متن‌های فارسی به صورت ??? نمایش داده می‌شوند

**راه حل:**
```sql
-- بررسی charset فعلی
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';

-- اصلاح اگر نیاز باشد
SET NAMES utf8mb4;
```

### مشکل ۲: خطای "Incorrect string value"

**راه حل:**
- اطمینان از utf8mb4 بودن جداول
- اجرای اسکریپت مایگریشن مجدد

### مشکل ۳: Connection charset اشتباه

**راه حل:**
- بررسی تنظیمات `init_command` در Django
- راه‌اندازی مجدد MySQL

### مشکل ۴: مایگریشن Django با خطا مواجه می‌شود

**راه حل:**
```bash
# پاک کردن cache
python manage.py migrate --fake-initial

# یا ریست کامل
python manage.py reset_db  # نیاز به django-extensions
python manage.py migrate
```

## تست نهایی

پس از تکمیل تمام مراحل، باید:

1. ✅ اسکریپت تست بدون خطا اجرا شود
2. ✅ متن‌های فارسی در admin panel صحیح نمایش داده شوند  
3. ✅ داده‌های فارسی در API درست برگردانده شوند
4. ✅ جستجوی فارسی کار کند

## نکات امنیتی

1. **رمز عبور قوی** برای کاربران دیتابیس استفاده کنید
2. **دسترسی‌های حداقلی** به کاربران دیتابیس بدهید  
3. **Backup منظم** از دیتابیس تهیه کنید
4. **SSL/TLS** برای اتصالات production فعال کنید

## منابع مفید

- [MySQL UTF-8 Documentation](https://dev.mysql.com/doc/refman/8.0/en/charset-unicode-utf8mb4.html)
- [Django Database Configuration](https://docs.djangoproject.com/en/stable/ref/settings/#databases)
- [Persian Text in MySQL](https://wiki.mysql.com/index.php/MySQL_Unicode)

---

**نکته:** این راهنما برای حل کامل مشکل نمایش متن‌های فارسی در MySQL طراحی شده است. در صورت بروز مشکل، می‌توانید مراحل را مجدد بررسی کنید.