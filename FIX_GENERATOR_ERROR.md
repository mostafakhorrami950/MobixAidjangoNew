# حل مشکل "Generator Already Executing"

## مشکل
خطای `generator already executing` در هنگام استفاده از streaming responses رخ می‌دهد.

## علت
این خطا زمانی اتفاق می‌افتد که:
1. یک generator function چندین بار فراخوانی می‌شود
2. streaming request قبلی هنوز تمام نشده و درخواست جدیدی ارسال می‌شود
3. reader های قبلی به درستی close نشده‌اند

## راه حل‌های اعمال شده

### 1. Backend (ai_models/services.py)
```python
def stream_text_response(self, ...):
    # Create a new generator function each time
    def create_generator():
        # Generator logic here
        
    # Return fresh generator each time
    return create_generator()
```

### 2. Frontend (static/chatbot/js/messaging.js)
```javascript
// Check and abort previous streaming
if (abortController && !abortController.signal.aborted) {
    abortController.abort();
    await new Promise(resolve => setTimeout(resolve, 100));
}

// Track reader state
let readerClosed = false;

// Check reader state before operations
if (readerClosed || abortController.signal.aborted) {
    return;
}
```

### 3. محافظت‌های اضافی
- پاک‌سازی streaming elements قبل از شروع جدید
- مدیریت صحیح abort controller ها
- تابع `cleanupStreamingState()` برای پاک‌سازی کامل

## آزمایش راه حل

برای آزمایش اینکه مشکل حل شده:

```bash
python test_chat_fixes.py
```

اگر test موفق بود، streaming باید بدون خطا کار کند.

## استفاده صحیح

### در JavaScript:
```javascript
// همیشه قبل از streaming جدید، قبلی را متوقف کنید
if (abortController) {
    abortController.abort();
}

// منتظر بمانید تا cleanup کامل شود
await new Promise(resolve => setTimeout(resolve, 100));

// سپس streaming جدید را شروع کنید
```

### در Python:
```python
# هر بار generator جدید ایجاد کنید، از همان generator استفاده مجدد نکنید
def get_stream():
    return service.stream_text_response(model, messages)

# نه این:
# generator = service.stream_text_response(model, messages)
# for chunk in generator:  # اولین استفاده
# for chunk in generator:  # خطا: generator already executing
```

## نکات مهم

1. **هرگز generator را دوبار استفاده نکنید**
2. **همیشه abortController قبلی را clear کنید**
3. **از cleanupStreamingState() در error handling استفاده کنید**
4. **منتظر بمانید تا streaming قبلی کاملاً تمام شود**

## اگر همچنان خطا داشتید

اگر بعد از این تغییرات همچنان خطا دارید:

1. Browser cache را پاک کنید
2. Hard refresh کنید (Ctrl+F5)
3. Console log ها را بررسی کنید
4. مطمئن شوید تمام تغییرات اعمال شده