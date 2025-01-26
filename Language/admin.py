from django.contrib import admin
from .models import Language

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)  # ستون‌هایی که در لیست نمایش داده شوند
    search_fields = ('name',)  # امکان جستجو بر اساس نام زبان
    ordering = ('name',)  # ترتیب نمایش رکوردها بر اساس نام زبان

# ثبت مدل Language در ادمین
admin.site.register(Language, LanguageAdmin)
