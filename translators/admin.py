# admin.py
from django.contrib import admin
from .models import Translator

class TranslatorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'nationality', 'rating')  # فیلدهای نمایش داده شده در لیست
    search_fields = ('first_name', 'last_name', 'nationality')  # فیلدهایی که برای جستجو در نظر گرفته شده‌اند
    list_filter = ('rating', 'nationality')  # فیلدهایی که می‌توانند برای فیلتر استفاده شوند
    ordering = ('-rating',)  # مرتب‌سازی به ترتیب نزولی بر اساس نمره
    list_per_page = 10  # تعداد نمایش هر صفحه از لیست

admin.site.register(Translator, TranslatorAdmin)
