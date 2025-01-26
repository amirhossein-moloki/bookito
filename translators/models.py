from django.db import models
from Language.models import Language
class Translator(models.Model):
    first_name = models.CharField(max_length=100)  # نام
    last_name = models.CharField(max_length=100)  # نام خانوادگی
    birth_date = models.DateField(null=True, blank=True)  # تاریخ تولد (اختیاری)
    nationality = models.CharField(max_length=100, null=True, blank=True)  # ملیت (اختیاری)
    languages = models.ManyToManyField(Language, blank=True)  # زبان‌هایی که مترجم به آن‌ها مسلط است
    biography = models.TextField(null=True, blank=True)  # بیوگرافی (اختیاری)
    profile_picture = models.ImageField(upload_to='translator_pictures/', null=True, blank=True)  # عکس پروفایل
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # نمره (بین 0.00 تا 10.00)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
