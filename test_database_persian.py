#!/usr/bin/env python
"""
اسکریپت تست برای بررسی اتصال دیتابیس و پشتیبانی از فارسی
"""
import os
import sys
import django
from pathlib import Path

# اضافه کردن مسیر پروژه
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

def test_database_connection():
    """تست اتصال به دیتابیس"""
    print("🔗 تست اتصال به دیتابیس...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ اتصال به دیتابیس موفقیت‌آمیز است")
                return True
            else:
                print("❌ مشکل در اتصال به دیتابیس")
                return False
    except Exception as e:
        print(f"❌ خطا در اتصال به دیتابیس: {e}")
        return False

def test_database_charset():
    """بررسی charset دیتابیس"""
    print("\n🔤 بررسی charset دیتابیس...")
    try:
        with connection.cursor() as cursor:
            # بررسی charset کلی
            cursor.execute("SHOW VARIABLES LIKE 'character_set%'")
            charset_vars = cursor.fetchall()
            
            print("تنظیمات character set:")
            for var_name, value in charset_vars:
                print(f"  {var_name}: {value}")
            
            # بررسی collation
            cursor.execute("SHOW VARIABLES LIKE 'collation%'")
            collation_vars = cursor.fetchall()
            
            print("\nتنظیمات collation:")
            for var_name, value in collation_vars:
                print(f"  {var_name}: {value}")
                
            return True
    except Exception as e:
        print(f"❌ خطا در بررسی charset: {e}")
        return False

def test_persian_text_storage():
    """تست ذخیره و بازیابی متن فارسی"""
    print("\n📝 تست ذخیره و بازیابی متن فارسی...")
    
    test_persian_texts = [
        "سلام دنیا! این یک تست فارسی است",
        "نام: علی احمدی",
        "شماره تلفن: ۰۹۱۲۳۴۵۶۷۸۹",
        "پیام: با موفقیت ثبت شد! ✅",
        "تاریخ: ۱۴۰۳/۰۶/۲۹",
        "🚀 تست ایموجی و نمادهای خاص: ⭐ 🌟 💫"
    ]
    
    try:
        # ایجاد کاربر تست با متن فارسی
        test_phone = "09123456789"
        
        # حذف کاربر قبلی اگر وجود دارد
        User.objects.filter(phone_number=test_phone).delete()
        
        for i, text in enumerate(test_persian_texts):
            test_user = User.objects.create_user(
                phone_number=f"0912345678{i}",
                name=text,
                username=f"0912345678{i}"
            )
            
            # بازیابی کاربر
            retrieved_user = User.objects.get(phone_number=f"0912345678{i}")
            
            print(f"  متن اصلی: {text}")
            print(f"  متن ذخیره شده: {retrieved_user.name}")
            
            if text == retrieved_user.name:
                print(f"  ✅ متن #{i+1} با موفقیت ذخیره و بازیابی شد")
            else:
                print(f"  ❌ مشکل در ذخیره متن #{i+1}")
                return False
            
            print("  " + "─" * 50)
        
        # پاک کردن داده‌های تست
        User.objects.filter(phone_number__startswith="091234567").delete()
        print("\n🧹 داده‌های تست پاک شدند")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست متن فارسی: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_tables_charset():
    """بررسی charset جداول"""
    print("\n🗃️  بررسی charset جداول...")
    try:
        with connection.cursor() as cursor:
            # دریافت نام دیتابیس
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            
            if not db_name:
                print("❌ نام دیتابیس یافت نشد")
                return False
            
            print(f"دیتابیس فعلی: {db_name}")
            
            # بررسی charset جداول
            cursor.execute("""
                SELECT TABLE_NAME, TABLE_COLLATION 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """, [db_name])
            
            tables = cursor.fetchall()
            utf8mb4_count = 0
            total_count = len(tables)
            
            print(f"\nجداول موجود ({total_count} جدول):")
            for table_name, collation in tables:
                status = "✅" if collation and "utf8mb4" in collation else "❌"
                print(f"  {status} {table_name}: {collation}")
                if collation and "utf8mb4" in collation:
                    utf8mb4_count += 1
            
            print(f"\nخلاصه: {utf8mb4_count}/{total_count} جدول از utf8mb4 استفاده می‌کنند")
            
            return utf8mb4_count == total_count
            
    except Exception as e:
        print(f"❌ خطا در بررسی جداول: {e}")
        return False

def main():
    """تابع اصلی تست"""
    print("🧪 شروع تست دیتابیس برای پشتیبانی از فارسی")
    print("=" * 60)
    
    tests_results = []
    
    # تست اتصال
    tests_results.append(("اتصال دیتابیس", test_database_connection()))
    
    # تست charset
    tests_results.append(("تنظیمات charset", test_database_charset()))
    
    # تست جداول
    tests_results.append(("charset جداول", test_database_tables_charset()))
    
    # تست متن فارسی
    tests_results.append(("ذخیره متن فارسی", test_persian_text_storage()))
    
    # نتیجه کلی
    print("\n" + "=" * 60)
    print("📊 گزارش نهایی:")
    
    passed_tests = 0
    for test_name, result in tests_results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"  {test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nنتیجه کلی: {passed_tests}/{len(tests_results)} تست موفقیت‌آمیز")
    
    if passed_tests == len(tests_results):
        print("🎉 تمام تست‌ها موفقیت‌آمیز بودند! دیتابیس شما آماده استفاده از متن‌های فارسی است.")
    else:
        print("⚠️  برخی تست‌ها ناموفق بودند. لطفاً مشکلات را برطرف کنید.")
        
        print("\n💡 راهنمای رفع مشکل:")
        print("1. اطمینان حاصل کنید که MySQL با تنظیمات utf8mb4 نصب شده است")
        print("2. فایل mysql_utf8mb4_migration.sql را اجرا کنید")
        print("3. متغیرهای محیطی MySQL را در فایل .env تنظیم کنید")
        print("4. مایگریشن‌های Django را اجرا کنید: python manage.py migrate")

if __name__ == "__main__":
    main()