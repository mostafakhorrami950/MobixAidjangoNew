# راهنمای سریع استفاده از PyMySQL

PyMySQL یک درایور خالص پایتون برای MySQL است که بر خلاف mysqlclient نیاز به نصب dependencies سیستم ندارد. این آن را برای هاست‌های مشترک مناسب می‌کند.

## مزایای PyMySQL:
- ✅ بدون نیاز به dependencies سیستم
- ✅ نصب آسان در هاست‌های مشترک
- ✅ پشتیبانی کامل از UTF-8/UTF-8MB4
- ✅ سازگاری کامل با Django

## مراحل راه‌اندازی:

### 1. نصب PyMySQL
```bash
pip install PyMySQL==1.1.0
```

### 2. تنظیم فایل .env
```bash
# کپی کردن فایل نمونه
cp .env.mysql.example .env

# ویرایش متغیرهای محیطی
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_database_user
MYSQL_PASSWORD=your_database_password
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
```

### 3. ایجاد دیتابیس MySQL
دیتابیس خود را با charset صحیح ایجاد کنید:
```sql
CREATE DATABASE your_database_name 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### 4. اجرای مایگریشن‌ها
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. تست سیستم
```bash
python test_database_persian.py
```

## تفاوت‌های مهم با mysqlclient:

| ویژگی | PyMySQL | mysqlclient |
|--------|---------|-------------|
| نصب | آسان (pip فقط) | نیاز به dependencies سیستم |
| عملکرد | کمی کندتر | سریع‌تر |
| سازگاری | خالص پایتون | C extension |
| هاست مشترک | ✅ مناسب | ❌ مشکل‌دار |

## استفاده در هاست‌های مختلف:

### هاست‌های مشترک
```bash
# فقط نصب PyMySQL کافی است
pip install PyMySQL
```

### VPS/Dedicated
```bash
# می‌توانید از هر دو استفاده کنید
pip install PyMySQL  # راحت‌تر
# یا
pip install mysqlclient  # سریع‌تر (نیاز به dependencies)
```

## عیب‌یابی:

### مشکل: "No module named 'MySQLdb'"
```python
import pymysql
pymysql.install_as_MySQLdb()
```
این کد در settings.py اضافه شده است.

### مشکل: Connection timeout
در فایل .env timeout ها را افزایش دهید:
```env
# یا در OPTIONS دیتابیس timeout ها تنظیم شده‌اند
```

### مشکل: charset مناسب نیست
اطمینان حاصل کنید دیتابیس با utf8mb4 ایجاد شده:
```sql
ALTER DATABASE your_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## نکات بهینه‌سازی:

1. **Connection Pool**: PyMySQL connection pooling ندارد، Django خودش مدیریت می‌کند
2. **Timeout Settings**: timeout های مناسب در settings تنظیم شده‌اند
3. **Charset**: همیشه utf8mb4 استفاده کنید
4. **Collation**: utf8mb4_unicode_ci برای فارسی مناسب است

## تست سریع:

```python
python manage.py shell

# تست اتصال
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 'سلام PyMySQL!' as test")
result = cursor.fetchone()
print(result[0])  # باید "سلام PyMySQL!" چاپ کند
```

## استفاده در Production:

PyMySQL برای production نیز مناسب است، اما برای high-traffic سایت‌ها ممکن است mysqlclient عملکرد بهتری داشته باشد.

**نتیجه:** PyMySQL بهترین انتخاب برای هاست‌های مشترک و پروژه‌های متوسط است.