کتاب‌فروشی آنلاین (Book Store)

این پروژه یک کتاب‌فروشی آنلاین است که با استفاده از Django و Django REST Framework پیاده‌سازی شده است. کدهای این پروژه برای عموم آزاد بوده و می‌توانید برای ایجاد تغییرات درخواست (Pull Request) ارسال کنید.

ویژگی‌ها

مدیریت کاربران و احراز هویت با JWT

سیستم پرداخت آنلاین با زرین‌پال

یکپارچه‌سازی با APIهای پستکس و زرین‌پال (نیازمند کلید API)

مدیریت سفارشات و سبد خرید

امکان دسته‌بندی و جستجوی کتاب‌ها

مستندسازی API با Swagger و ReDoc

امنیت بهینه‌شده شامل CSRF، Secure Cookies و HSTS

نحوه نصب و اجرا

ریپوزیتوری را کلون کنید:

git clone https://github.com/amirhossein-moloki/bookito.git
cd bookito

یک محیط مجازی ایجاد کنید و وابستگی‌ها را نصب کنید:

python -m venv venv
source venv/bin/activate  # در ویندوز: venv\Scripts\activate
pip install -r requirements.txt

تنظیمات محیطی را مقداردهی کنید (مانند DJANGO_SECRET_KEY، ZARINPAL_MERCHANT_ID، و کلیدهای API پستکس و زرین‌پال).

مهاجرت‌های پایگاه داده را اعمال کنید:

python manage.py migrate

سرور را اجرا کنید:

python manage.py runserver

مستندات API

برای مشاهده مستندات API، پس از اجرای سرور، به این مسیرها مراجعه کنید:

Swagger UI: http://127.0.0.1:8000/swagger/

ReDoc: http://127.0.0.1:8000/redoc/

مشارکت در پروژه

شما می‌توانید این ریپوزیتوری را فورک کرده و تغییرات خود را ایجاد کنید.

پس از اعمال تغییرات، یک Pull Request ارسال کنید.

برای ارتباط و پیشنهادات، با ایمیل زیر در تماس باشید:
amirh.moloki@gmail.com

لایسنس

این پروژه تحت لایسنس MIT منتشر شده است و استفاده از آن برای عموم آزاد است.