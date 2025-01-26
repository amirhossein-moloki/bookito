from django.contrib import admin
from .models import Publisher

class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'established_date', 'country', 'email', 'phone_number')  # ستون‌های نمایش داده شده در لیست
    search_fields = ('name', 'email', 'country')  # امکان جستجو بر اساس نام، ایمیل و کشور
    list_filter = ('country', 'established_date')  # فیلتر کردن بر اساس کشور و تاریخ تأسیس
    ordering = ('name',)  # ترتیب نمایش براساس نام
    fields = ('name', 'established_date', 'address', 'website', 'email', 'phone_number', 'country', 'description', 'logo', 'social_media_links')  # فیلدهای نمایش داده شده در فرم

# ثبت مدل Publisher در ادمین
admin.site.register(Publisher, PublisherAdmin)
