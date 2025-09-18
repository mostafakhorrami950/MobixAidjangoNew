# راهنمای عیب‌یابی تولید تصویر

## مشکلات حل شده:

### 1. رفع UnboundLocalError
✅ **حل شد**: متغیر `last_uploaded_image` اکنون به درستی مقداردهی اولیه می‌شود

### 2. ادغام خودکار تصاویر
✅ **حل شد**: دیگر نیازی به نوشتن کلمه "ادغام" نیست
- تصاویر خودکار با آخرین تصویر تولید شده ادغام می‌شوند
- پیام خودکار "(با تصویر قبلی)" اضافه می‌شود

### 3. رفرش خودکار پس از تولید تصویر
✅ **حل شد**: صفحه خودکار پس از تکمیل تولید تصویر رفرش می‌شود
- رفرش فقط برای image editing chatbots فعال است
- رفرش 1.5 ثانیه پس از تکمیل streaming اتفاق می‌افتد
- نمایش notification مناسب قبل از رفرش
- پشتیبانی از حالت abort (توقف کاربر) برای رفرش

## تغییرات اعمال شده:

### Backend (Django)
- **فایل**: `chatbot/views.py`
- **خط 493**: اضافه شدن `last_uploaded_image = None`
- **خط 496-521**: حذف نیاز به کلمه "ادغام" و خودکار کردن ادغام

### Frontend (JavaScript)
- **فایل**: `static/chatbot/js/messaging.js`
- **خط 150-160**: رفرش خودکار پس از تکمیل تولید تصویر (1.5 ثانیه تأخیر)
- **خط 292-308**: رفرش در حالت abort (streaming reader)
- **خط 375-391**: رفرش در حالت abort (catch block)
- **خط 521-546**: اضافه شدن debug logs برای تصاویر
- **خط 1131-1132**: بهبود پیام موفقیت با اعلام رفرش

### Styles (CSS)
- **فایل**: `static/css/chat.css`
- **خط 537-565**: اضافه شدن استایل‌های مناسب برای تصاویر

## چگونه تست کنیم:

1. **راه‌اندازی سرور**:
```bash
python manage.py runserver
```

2. **باز کردن Image Editing Chatbot**:
   - در interface، یک image editing chatbot انتخاب کنید
   - تصویری آپلود کنید
   - پیامی ارسال کنید

3. **بررسی Console Browser**:
   - F12 > Console
   - باید لاگ‌هایی مانند این ببینید:
   ```
   Processing images for display: [...]
   Image 1 URL: /media/...
   Generated image content HTML: ...
   Image 1 loaded successfully
   ```

4. **تست ادغام خودکار**:
   - پس از تولید تصویر اول، تصویر جدید آپلود کنید
   - بدون نوشتن "ادغام"، باید تصاویر ادغام شوند
   - در پیام "با تصویر قبلی" نمایش داده می‌شود

5. **تست رفرش خودکار**:
   - تولید تصویر را تا پایان منتظر بمانید
   - بعد از تکمیل streaming، باید پیام "تصویر با موفقیت تولید شد!" ظاهر شود
   - در زیر پیام "صفحه در حال به‌روزرسانی..." نمایش داده می‌شود
   - پس از 1.5 ثانیه صفحه رفرش می‌شود

## مشکلات احتمالی و راه‌حل:

### اگر تصاویر نمایش داده نمی‌شوند:
1. **بررسی Console**:
   ```javascript
   // در Console مرورگر
   console.log('Checking image elements:', document.querySelectorAll('.image-container img'));
   ```

2. **بررسی مسیرهای فایل**:
   - مسیر `/media/` موجود است؟
   - فایل‌های تصویر در `MEDIA_ROOT` ذخیره می‌شوند؟

3. **بررسی CORS و Static Files**:
   ```python
   # در settings.py
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   ```

### اگر ادغام کار نمی‌کند:
1. **بررسی لاگ سرور**:
   ```
   Processing image editing request...
   Found last generated image: ...
   ```

2. **بررسی کد Backend**:
   - آیا `last_image_message` درست یافت می‌شود؟
   - آیا فایل تصویر موجود است؟

### اگر صفحه همچنان رفرش می‌شود:
1. **غیرفعال کردن رفرش دستی**:
   - کدهای `location.reload()` را حذف کنید
   - از `addMessageToChat()` به جای reload استفاده کنید

## فایل‌های مرتبط:
- `chatbot/views.py` - منطق backend
- `static/chatbot/js/messaging.js` - کنترل frontend
- `static/chatbot/js/messages.js` - نمایش پیام‌ها
- `static/css/chat.css` - استایل‌ها