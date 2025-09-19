# راهنمای سیستم مدیریت پلن‌های پیش‌فرض اشتراک

این راهنما نحوه استفاده از سیستم جدید مدیریت پلن‌های پیش‌فرض اشتراک را توضیح می‌دهد.

## ✨ ویژگی‌های جدید

### 🎯 مدیریت از پنل ادمین
- تنظیم پلن پیش‌فرض برای کاربران جدید
- تنظیم پلن fallback پس از انقضای اشتراک
- مدیریت آسان از طریق Django Admin

### 🔄 مدیریت خودکار انقضا
- بررسی خودکار اشتراک‌های منقضی شده
- تخصیص خودکار پلن fallback
- لاگ‌گیری کامل تمام عملیات

### 📊 آمارگیری و مانیتورینگ
- آمار کاربران با/بدون اشتراک
- آمار بر اساس نوع پلن
- تشخیص و رفع مشکلات

## 🚀 راه‌اندازی اولیه

### 1. اجرای مایگریشن

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. راه‌اندازی تنظیمات پیش‌فرض

```bash
# راه‌اندازی خودکار با پلن Basic
python manage.py manage_subscriptions --action=setup_defaults

# یا مشخص کردن پلن دلخواه
python manage.py manage_subscriptions --action=setup_defaults --plan-name="Free"
```

### 3. بررسی تنظیمات

```bash
python manage.py manage_subscriptions --action=validate
```

## 📋 مدیریت از پنل ادمین

### دسترسی به تنظیمات

1. وارد Django Admin شوید
2. بخش **Subscriptions** > **تنظیمات پیش‌فرض اشتراک** را باز کنید

### انواع تنظیمات

#### 👤 پلن پیش‌فرض کاربران جدید
- پلنی که به صورت خودکار به کاربران جدید تخصیص می‌یابد
- معمولاً یک پلن رایگان یا Basic

#### ⏰ پلن پیش‌فرض پس از انقضا
- پلنی که پس از انقضای اشتراک پولی تخصیص می‌یابد
- معمولاً همان پلن Basic یا Free

### ایجاد تنظیم جدید

1. **Add تنظیمات پیش‌فرض اشتراک** را کلیک کنید
2. **نوع تنظیم** را انتخاب کنید
3. **پلن اشتراک** مورد نظر را انتخاب کنید
4. **فعال** را تیک بزنید
5. در صورت نیاز **توضیح** اضافه کنید
6. ذخیره کنید

## 🛠 مدیریت از خط فرمان

### دستورات اصلی

```bash
# نمایش آمار اشتراک‌ها
python manage.py manage_subscriptions --action=stats

# بررسی تنظیمات
python manage.py manage_subscriptions --action=validate

# بررسی اشتراک‌های منقضی شده
python manage.py manage_subscriptions --action=check_expired

# تخصیص پلن پیش‌فرض به کاربران بدون اشتراک
python manage.py manage_subscriptions --action=assign_defaults

# رفع مشکل کاربران بدون اشتراک
python manage.py manage_subscriptions --action=fix_users_without_subscription
```

### حالت تست (Dry Run)

```bash
# اجرای تست بدون اعمال تغییرات
python manage.py manage_subscriptions --action=check_expired --dry-run
```

## 📊 نظارت و مانیتورینگ

### آمار کلی سیستم

```bash
python manage.py manage_subscriptions --action=stats
```

خروجی نمونه:
```
📊 آمار اشتراک‌ها:
👥 کل کاربران: 1250
✅ کاربران با اشتراک: 1200
❌ کاربران بدون اشتراک: 50
🟢 اشتراک‌های فعال: 1180
🔴 اشتراک‌های منقضی: 20

📈 آمار بر اساس نوع اشتراک:
  Basic: 800 کاربر
  Premium: 300 کاربر
  Pro: 80 کاربر
```

### اعتبارسنجی تنظیمات

```bash
python manage.py manage_subscriptions --action=validate
```

## 🔧 عیب‌یابی مشکلات رایج

### مشکل: کاربران جدید اشتراک دریافت نمی‌کنند

**بررسی:**
```bash
python manage.py manage_subscriptions --action=validate
```

**راه‌حل:**
1. اطمینان از وجود تنظیم فعال برای کاربران جدید
2. بررسی فعال بودن پلن انتخاب شده
3. در صورت نیاز ایجاد تنظیمات جدید

### مشکل: کاربران موجود اشتراک ندارند

**بررسی:**
```bash
python manage.py manage_subscriptions --action=stats
```

**راه‌حل:**
```bash
python manage.py manage_subscriptions --action=fix_users_without_subscription
```

### مشکل: اشتراک‌های منقضی شده پردازش نمی‌شوند

**بررسی:**
```bash
python manage.py manage_subscriptions --action=check_expired --dry-run
```

**راه‌حل:**
```bash
python manage.py manage_subscriptions --action=check_expired
```

## 🤖 اتوماسیون با Cron

برای اجرای خودکار پردازش اشتراک‌های منقضی شده:

```bash
# ایجاد cron job (روزانه ساعت 2:00 صبح)
0 2 * * * cd /path/to/project && python manage.py manage_subscriptions --action=check_expired
```

## 🔒 امنیت و بهترین روش‌ها

### 1. محدودیت دسترسی Admin
- فقط مدیران ارشد دسترسی به تغییر تنظیمات داشته باشند
- تغییرات مهم را لاگ کنید

### 2. پشتیبان‌گیری
- قبل از تغییرات عمده، پشتیبان از دیتابیس تهیه کنید
- ابتدا در محیط تست آزمایش کنید

### 3. مانیتورینگ
- آمار روزانه از سیستم بگیرید
- لاگ‌های خطا را بررسی کنید

## 📈 گسترش سیستم

### اضافه کردن انواع تنظیمات جدید

1. در فایل `models.py` به `SETTING_TYPES` اضافه کنید
2. متدهای جدید در کلاس `DefaultSubscriptionSettings` ایجاد کنید
3. مایگریشن اجرا کنید

### اضافه کردن قوانین پیچیده‌تر

می‌توانید در کلاس `SubscriptionManager` منطق پیچیده‌تری اضافه کنید:
- تخصیص بر اساس تاریخ عضویت
- تخصیص بر اساس محل جغرافیایی
- تخصیص بر اساس نوع کاربر

## 📞 پشتیبانی

در صورت بروز مشکل:
1. ابتدا `--validate` را اجرا کنید
2. لاگ‌های Django را بررسی کنید
3. `--dry-run` برای تست استفاده کنید
4. در صورت نیاز از طریق پنل ادمین تنظیمات را بررسی کنید

---

**نکته:** این سیستم به گونه‌ای طراحی شده که حداقل تأثیر منفی روی عملکرد سایت داشته باشد و تمام عملیات مهم لاگ می‌شوند.