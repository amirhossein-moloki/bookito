from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from books.models import Book

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews', verbose_name="کتاب")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="کاربر")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="نظر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['book', 'user'],
                name='unique_review_per_book_per_user'
            )
        ]
        ordering = ['-created_at']
        verbose_name = "نقد و بررسی"
        verbose_name_plural = "نقد و بررسی‌ها"

    def __str__(self):
        return f'نظر {self.user.username} برای کتاب {self.book.title}'
