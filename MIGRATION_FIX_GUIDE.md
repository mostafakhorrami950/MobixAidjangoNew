# راهنمای حل مشکل مایگریشن‌ها در Production

## 🚨 مشکل
خطای مایگریشن Django در سرور production:
```
NodeNotFoundError: Migration chatbot.0031_messagefile dependencies reference nonexistent parent node ('chatbot', '0030_add_disabled_field_to_chatmessage')
```

## 🔍 تشخیص مشکل
مایگریشن `0031_messagefile` به مایگریشن `0030_add_disabled_field_to_chatmessage` وابسته است که ممکن است در سرور production موجود نباشد یا نام متفاوتی داشته باشد.

## ✅ راه حل اعمال شده

### 1. بررسی فایل‌های موجود
در development environment، فایل‌های مایگریشن اصلاح شدند:

- ✅ `0030_add_disabled_field_to_chatmessage.py` - موجود است
- ❌ `0031_messagefile.py` - حذف شد
- ✅ `0032_limitationmessage.py` - وابستگی اصلاح شد
- ✅ `0033_add_auto_generate_title_field.py` - صحیح است
- ✅ `0034_messagefile.py` - جدید ایجاد شد

### 2. تغییرات انجام شده

#### الف) اصلاح مایگریشن 0032
```python
# قبل از اصلاح
dependencies = [
    ("chatbot", "0031_messagefile"),
]

# بعد از اصلاح  
dependencies = [
    ("chatbot", "0030_add_disabled_field_to_chatmessage"),
]
```

#### ب) ایجاد مایگریشن جدید 0034
- مایگریشن `MessageFile` دوباره در فایل `0034_messagefile.py` ایجاد شد
- وابستگی آن به `0033_add_auto_generate_title_field` تنظیم شد

## 🚀 مراحل اعمال در Production

### گام 1: بررسی مایگریشن‌های موجود در سرور
```bash
python manage.py showmigrations chatbot
```

### گام 2: یکی از روش‌های زیر را انتخاب کنید

#### روش A: اعمال مایگریشن‌های اصلاح شده (پیشنهادی)

1. فایل‌های مایگریشن اصلاح شده را آپلود کنید:
   - `chatbot/migrations/0032_limitationmessage.py`
   - `chatbot/migrations/0034_messagefile.py`

2. اعمال مایگریشن‌ها:
```bash
# خشک تست کردن
python manage.py migrate --dry-run

# اعمال واقعی
python manage.py migrate
```

#### روش B: اعمال دستی مایگریشن (در صورت مشکل)

اگر هنوز مشکل دارید، این دستورات را اجرا کنید:

```bash
# علامت‌گذاری مایگریشن‌هایی که مشکل دارند
python manage.py migrate chatbot 0030 --fake

# ایجاد جدول‌های جدید به صورت دستی (اگر نیاز باشد)
python manage.py sqlmigrate chatbot 0032
python manage.py sqlmigrate chatbot 0034

# اعمال مایگریشن‌ها
python manage.py migrate chatbot
```

#### روش C: ریست کامل مایگریشن‌ها (آخرین راه حل)

⚠️ **احتیاط**: این روش فقط اگر داده‌های مهمی ندارید استفاده کنید:

```bash
# بکاپ دیتابیس
pg_dump your_database > backup.sql

# حذف مایگریشن‌های مشکل‌دار
rm chatbot/migrations/0031_messagefile.py

# ایجاد مایگریشن جدید
python manage.py makemigrations chatbot

# اعمال مایگریشن‌ها
python manage.py migrate
```

## 🔍 بررسی صحت اعمال

بعد از اعمال، این موارد را بررسی کنید:

```bash
# بررسی وضعیت مایگریشن‌ها
python manage.py showmigrations chatbot

# تست ایجاد MessageFile
python manage.py shell
>>> from chatbot.models import MessageFile
>>> MessageFile.objects.all()

# تست ایجاد LimitationMessage
>>> from chatbot.models import LimitationMessage
>>> LimitationMessage.objects.all()
```

## 📋 چک لیست

- [ ] بکاپ از دیتابیس تهیه شده
- [ ] فایل‌های مایگریشن اصلاح شده آپلود شده
- [ ] `python manage.py migrate --dry-run` موفق است
- [ ] `python manage.py migrate` اجرا شده
- [ ] `python manage.py showmigrations` همه مایگریشن‌ها را applied نشان می‌دهد
- [ ] مدل‌های جدید قابل import و استفاده هستند

## 🆘 در صورت بروز مشکل

اگر مشکلی پیش آمد:

1. دیتابیس را از بکاپ بازگردانی کنید
2. لاگ‌های خطا را چک کنید
3. دستور `python manage.py showmigrations` را اجرا کنید
4. با تیم پشتیبانی تماس بگیرید

## 📝 نکات مهم

- همیشه قبل از اعمال مایگریشن‌ها بکاپ تهیه کنید
- ابتدا در محیط staging تست کنید
- در ساعات کم‌ترافیک اعمال کنید
- مانیتورینگ را در طول فرآیند فعال نگه دارید