from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=255)  # نام انتشارات
    established_date = models.DateField(null=True, blank=True)  # تاریخ تأسیس
    address = models.TextField(null=True, blank=True)  # آدرس
    website = models.URLField(null=True, blank=True)  # وب‌سایت
    email = models.EmailField(null=True, blank=True)  # ایمیل
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # شماره تلفن
    country = models.CharField(max_length=100, null=True, blank=True)  # کشور
    description = models.TextField(null=True, blank=True)  # توضیحات مختصر درباره انتشارات
    logo = models.ImageField(upload_to='publishers/logos/', null=True, blank=True)  # لوگو انتشارات
    social_media_links = models.JSONField(null=True, blank=True)  # لینک‌های شبکه‌های اجتماعی (اختیاری)

    def __str__(self):
        return self.name
