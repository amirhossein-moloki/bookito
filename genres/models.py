from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)  # نام ژانر
    description = models.TextField(blank=True, null=True)  # توضیحات
    created_at = models.DateTimeField(auto_now_add=True)  # تاریخ ایجاد

    def __str__(self):
        return self.name
