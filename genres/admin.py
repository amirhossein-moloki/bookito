from django.contrib import admin
from .models import Genre

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')  # ستون‌هایی که در لیست نمایش داده شوند
    search_fields = ('name',)  # امکان جستجو بر اساس نام ژانر
    ordering = ('created_at',)  # ترتیب نمایش رکوردها بر اساس تاریخ ایجاد
    list_filter = ('created_at',)  # فیلتر کردن بر اساس تاریخ ایجاد

# ثبت مدل Genre در ادمین
admin.site.register(Genre, GenreAdmin)
