# راهنمای حل مشکل فایل‌های استاتیک صفحه ادمین Django

مشکل عدم لود شدن فایل‌های استاتیک در صفحه ادمین Django یکی از مشکلات رایج در deployment است. این راهنما راه‌حل‌های کاملی ارائه می‌دهد.

## 🔍 تشخیص مشکل

### 1. اجرای دستور تشخیص:
```bash
python manage.py debug_static
```

### 2. بررسی دستی در مرورگر:
- وارد صفحه ادمین شوید: `/admin/`
- Developer Tools (F12) را باز کنید
- تب Network را بررسی کنید
- خطاهای 404 برای فایل‌های CSS/JS را جستجو کنید

## ⚙️ مراحل حل مشکل

### مرحله 1: اجرای collectstatic

```bash
# جمع‌آوری تمام فایل‌های استاتیک
python manage.py collectstatic --noinput

# یا برای پاک کردن و جمع‌آوری مجدد
python manage.py collectstatic --clear --noinput
```

### مرحله 2: بررسی ساختار فولدرها

پس از collectstatic باید ساختار زیر وجود داشته باشد:
```
project/
├── staticfiles/           # فایل‌های جمع‌آوری شده
│   ├── admin/            # فایل‌های ادمین Django
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── css/              # فایل‌های پروژه
│   ├── js/
│   └── ...
├── static/               # فایل‌های اصلی پروژه
└── media/                # فایل‌های آپلود شده
```

### مرحله 3: تنظیمات development

در حالت development (DEBUG=True):

```python
# settings.py
DEBUG = True
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

```python
# urls.py - اضافه شده
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### مرحله 4: تنظیمات production

در حالت production (DEBUG=False):

```python
# settings.py
DEBUG = False
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise برای serving فایل‌های استاتیک
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# تنظیمات Whitenoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
```

## 🌐 تنظیمات وب‌سرور

### Nginx (پیشنهادی برای production)

```nginx
# /etc/nginx/sites-available/mobixai.ir
server {
    listen 80;
    server_name mobixai.ir www.mobixai.ir;

    # Static files - مستقیماً توسط Nginx
    location /static/ {
        alias /home/mobixtub/mobixai.ir/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        gzip on;
    }

    # Media files
    location /media/ {
        alias /home/mobixtub/mobixai.ir/media/;
        expires 7d;
    }

    # Django app
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

فعال‌سازی:
```bash
sudo ln -s /etc/nginx/sites-available/mobixai.ir /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Apache (جایگزین)

```apache
# /etc/apache2/sites-available/mobixai.ir.conf
<VirtualHost *:80>
    ServerName mobixai.ir
    ServerAlias www.mobixai.ir
    
    DocumentRoot /home/mobixtub/mobixai.ir
    
    # Static files
    Alias /static/ /home/mobixtub/mobixai.ir/staticfiles/
    <Directory "/home/mobixtub/mobixai.ir/staticfiles/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 30 days"
    </Directory>
    
    # Media files
    Alias /media/ /home/mobixtub/mobixai.ir/media/
    <Directory "/home/mobixtub/mobixai.ir/media/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 7 days"
    </Directory>
    
    # Django app
    ProxyPreserveHost On
    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

## 🧪 تست‌ها

### تست 1: دسترسی مستقیم
```bash
# تست دسترسی به فایل‌های استاتیک
curl -I http://your-domain.com/static/admin/css/base.css
# باید 200 OK برگرداند
```

### تست 2: Django shell
```python
python manage.py shell

from django.contrib.staticfiles import finders
from django.conf import settings

# بررسی یک فایل ادمین
admin_css = finders.find('admin/css/base.css')
print(f"Admin CSS path: {admin_css}")

# بررسی تنظیمات
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
```

### تست 3: مرورگر
1. وارد `/admin/` شوید
2. F12 را فشار دهید
3. تب Network را باز کنید
4. صفحه را refresh کنید
5. فایل‌های CSS/JS باید 200 status داشته باشند

## 🚨 رفع مشکلات رایج

### مشکل 1: فایل‌های ادمین یافت نمی‌شوند

**راه‌حل:**
```bash
# اطمینان از نصب کامل Django
pip install Django --upgrade

# جمع‌آوری مجدد فایل‌ها
python manage.py collectstatic --clear --noinput
```

### مشکل 2: مسیر STATIC_ROOT اشتباه

**راه‌حل:**
```python
# settings.py - مطمئن شوید مسیر صحیح است
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# نه این:
# STATIC_ROOT = '/wrong/path/'
```

### مشکل 3: مجوزهای فایل در سرور

**راه‌حل:**
```bash
# تنظیم مجوزهای صحیح
chmod -R 755 /home/mobixtub/mobixai.ir/staticfiles/
chown -R mobixtub:mobixtub /home/mobixtub/mobixai.ir/staticfiles/
```

### مشکل 4: Whitenoise کار نمی‌کند

**راه‌حل:**
```python
# settings.py - ترتیب middleware مهم است
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # باید اینجا باشد
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

### مشکل 5: فایل‌های پروژه یافت نمی‌شوند

**راه‌حل:**
```bash
# بررسی وجود فولدر static
ls -la static/

# اگر وجود ندارد، ایجاد کنید
mkdir -p static/css static/js static/img
```

## 📋 چک‌لیست نهایی

- [ ] `DEBUG = False` در production
- [ ] `collectstatic` اجرا شده
- [ ] فولدر `staticfiles` وجود دارد
- [ ] فایل‌های ادمین در `staticfiles/admin/` هستند
- [ ] `STATIC_URL` در settings تنظیم شده (`"/static/"`)
- [ ] `STATIC_ROOT` تنظیم شده
- [ ] Nginx/Apache پیکربندی شده
- [ ] مجوزهای فایل صحیح است
- [ ] تست مرورگر موفقیت‌آمیز است

## 🎯 نتیجه‌گیری

پس از اجرای تمام مراحل بالا:

1. **Development**: فایل‌های استاتیک توسط Django serve می‌شوند
2. **Production**: فایل‌های استاتیک توسط Nginx/Apache serve می‌شوند
3. **Admin panel**: کاملاً stylized و functional خواهد بود
4. **Performance**: بهبود قابل توجهی خواهید داشت

در صورت ادامه مشکل، لطفاً:
- خروجی `python manage.py debug_static` را بررسی کنید
- لاگ‌های Nginx/Apache را چک کنید
- Developer Tools مرورگر را بررسی کنید