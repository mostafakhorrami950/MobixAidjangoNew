# سیستم مدیریت تنظیمات Global فایل آپلود

این سند توضیح می‌دهد که چگونه سیستم جدید مدیریت تنظیمات global برای فایل آپلود پیاده‌سازی شده است.

## نمای کلی

سیستم جدید امکان مدیریت متمرکز تنظیمات فایل آپلود را از طریق admin panel فراهم می‌کند. این شامل محدودیت‌های حجم فایل، تعداد فایل، فرمت‌های مجاز و سایر تنظیمات عملکردی است.

## اجزای سیستم

### 1. Model: `GlobalSettings` (core/models.py)

```python
class GlobalSettings(models.Model):
    # File Upload Settings
    max_file_size_mb = models.PositiveIntegerField(default=10)
    max_files_per_message = models.PositiveIntegerField(default=5)
    allowed_file_extensions = models.TextField(default="txt,pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,webp")
    
    # Security Settings
    session_timeout_hours = models.PositiveIntegerField(default=24)
    
    # Performance Settings
    messages_per_page = models.PositiveIntegerField(default=50)
    api_requests_per_minute = models.PositiveIntegerField(default=60)
```

ویژگی‌های کلیدی:
- فقط یک instance از `GlobalSettings` مجاز است (singleton pattern)
- متدهای کمکی برای تبدیل داده‌ها (`get_max_file_size_bytes`, `get_allowed_extensions_list`)
- متد `get_settings()` برای دریافت instance فعال

### 2. Admin Interface (core/admin.py)

```python
@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    # Organized fieldsets for easy management
    # Prevents adding multiple instances
    # Prevents deletion of settings
```

ویژگی‌ها:
- fieldsetهای سازمان‌یافته برای دسته‌بندی تنظیمات
- محدود کردن اضافه کردن instance جدید
- جلوگیری از حذف تنظیمات

### 3. Service Layer: `GlobalFileService` (chatbot/file_services.py)

```python
class GlobalFileService:
    @staticmethod
    def validate_files(files):
        """Comprehensive validation for uploaded files"""
        
    @staticmethod
    def check_file_extension_allowed(file_extension):
        """Check if file extension is allowed"""
        
    @staticmethod
    def check_file_size_limit(file_size):
        """Check if file size is within global limit"""
```

متدهای کلیدی:
- `validate_files()`: اعتبارسنجی جامع فایل‌های آپلود شده
- `check_file_extension_allowed()`: بررسی فرمت فایل
- `check_file_size_limit()`: بررسی حجم فایل
- `check_files_count_per_message()`: بررسی تعداد فایل

### 4. API Endpoint

```
GET /chatbot/api/global-settings/
```

پاسخ JSON:
```json
{
    "max_file_size_mb": 10,
    "max_files_per_message": 5,
    "allowed_extensions": ["txt", "pdf", "doc", "docx", "jpg", "jpeg", "png", "gif", "webp"],
    "messages_per_page": 50,
    "api_requests_per_minute": 60
}
```

### 5. Frontend JavaScript (static/js/global-settings.js)

ویژگی‌ها:
- بارگیری خودکار تنظیمات از سرور
- اعتبارسنجی real-time فایل‌های انتخاب شده
- نمایش پیام‌های خطا به کاربر
- بروزرسانی خودکار ویژگی‌های فایل input

## نحوه استفاده

### 1. راه‌اندازی اولیه

```bash
# اجرای migration
python manage.py migrate

# ایجاد تنظیمات پیش‌فرض
python manage.py setup_global_settings
```

### 2. مدیریت از طریق Admin Panel

1. وارد admin panel شوید
2. به بخش "Core" → "Global Settings" بروید
3. تنظیمات را ویرایش کنید
4. تغییرات فوراً اعمال می‌شوند

### 3. استفاده در کد

```python
# دریافت تنظیمات
from chatbot.file_services import GlobalFileService

settings = GlobalFileService.get_global_settings()

# اعتبارسنجی فایل‌ها
files_valid, error_message = GlobalFileService.validate_files(uploaded_files)
if not files_valid:
    return JsonResponse({'error': error_message}, status=403)
```

### 4. استفاده در Frontend

```javascript
// فایل global-settings.js به صورت خودکار بارگیری می‌شود
// اعتبارسنجی فایل‌ها به صورت خودکار انجام می‌شود

// دسترسی دستی به تنظیمات
if (window.globalFileSettings) {
    const validation = window.globalFileSettings.validateFiles(files);
    if (!validation.valid) {
        console.error(validation.message);
    }
}
```

## تنظیمات پیش‌فرض

- **حداکثر حجم فایل**: 10 مگابایت
- **حداکثر تعداد فایل در هر پیام**: 5 عدد
- **فرمت‌های مجاز**: txt, pdf, doc, docx, xls, xlsx, jpg, jpeg, png, gif, webp
- **مهلت session**: 24 ساعت
- **پیام‌ها در هر صفحه**: 50 عدد
- **درخواست‌های API در دقیقه**: 60 عدد

## رابطه با سیستم Subscription

سیستم global settings به عنوان یک لایه پایه عمل می‌کند، در حالی که تنظیمات subscription می‌توانند محدودیت‌های بیشتری اعمال کنند:

1. ابتدا فایل‌ها بر اساس global settings اعتبارسنجی می‌شوند
2. سپس محدودیت‌های subscription (در صورت وجود) بررسی می‌شوند
3. محدودیت‌های subscription معمولاً سخت‌گیرانه‌تر هستند

## امنیت

- فقط کاربران وارد شده می‌توانند به API دسترسی داشته باشند
- فقط admin می‌تواند تنظیمات را تغییر دهد
- اعتبارسنجی فایل‌ها در سمت سرور و کلاینت انجام می‌شود
- فرمت‌های خطرناک به طور پیش‌فرض مسدود هستند

## نظارت و Logging

سیستم خطاهای مربوط به اعتبارسنجی فایل را log می‌کند:

```python
import logging
logger = logging.getLogger(__name__)
logger.error(f"File validation failed: {error_message}")
```

## Troubleshooting

### مشکلات رایج:

1. **API endpoint کار نمی‌کند**:
   - بررسی کنید که URL در `chatbot/urls.py` اضافه شده باشد
   - مطمئن شوید که کاربر login است

2. **تنظیمات اعمال نمی‌شوند**:
   - Cache مرورگر را پاک کنید
   - بررسی کنید که `GlobalSettings` instance فعال وجود دارد

3. **فایل‌های مجاز آپلود نمی‌شوند**:
   - تنظیمات `allowed_file_extensions` را بررسی کنید
   - مطمئن شوید که فایل در محدوده حجم مجاز است

### دستورات تشخیص:

```bash
# بررسی وجود GlobalSettings
python manage.py shell -c "from core.models import GlobalSettings; print(GlobalSettings.objects.count())"

# نمایش تنظیمات فعلی
python manage.py shell -c "from core.models import GlobalSettings; settings = GlobalSettings.get_settings(); print(f'Max size: {settings.max_file_size_mb}MB')"
```

## آینده و بهبودها

- افزودن cache برای بهبود performance
- امکان تنظیمات مخصوص هر domain
- گزارش‌گیری از الگوهای استفاده
- API برای تغییر تنظیمات از طریق کد