from django.contrib import admin
from .models import Discount

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage', 'start_date', 'end_date', 'is_active')  # ستون‌هایی که در لیست نمایش داده شوند
    search_fields = ('code',)  # امکان جستجو بر اساس کد تخفیف
    list_filter = ('is_active', 'start_date', 'end_date')  # فیلتر کردن بر اساس وضعیت فعال بودن و تاریخ‌ها
    ordering = ('-start_date',)  # ترتیب نمایش بر اساس تاریخ شروع تخفیف

# ثبت مدل Discount در ادمین
admin.site.register(Discount, DiscountAdmin)
