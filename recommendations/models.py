from django.db import models
from django.conf import settings
from books.models import Book

class BookRecommendation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_recommendations', verbose_name="کاربر")
    recommendations = models.ManyToManyField(Book, blank=True, verbose_name="کتاب‌های پیشنهادی")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "پیشنهاد کتاب"
        verbose_name_plural = "پیشنهادات کتاب"

    def __str__(self):
        return f"پیشنهادات برای {self.user.username}"
