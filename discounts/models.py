from django.db import models
from django.utils import timezone
from django.conf import settings
from books.models import Book, BookFormat, Genre
from authors.models import Author

class Discount(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', 'درصد'
        FIXED_AMOUNT = 'FIXED_AMOUNT', 'مبلغ ثابت'

    code = models.CharField(max_length=50, unique=True, verbose_name="کد تخفیف")
    type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE, verbose_name="نوع تخفیف")
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="مقدار (درصد یا مبلغ)")

    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # Usage Limits
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name="حداکثر تعداد استفاده (کل)")
    times_used = models.PositiveIntegerField(default=0, editable=False, verbose_name="تعداد دفعات استفاده شده")
    max_uses_per_customer = models.PositiveIntegerField(null=True, blank=True, verbose_name="حداکثر استفاده برای هر مشتری")

    # Conditions
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="حداقل مبلغ خرید")

    # Applicability (if all are blank, it's global)
    applicable_books = models.ManyToManyField(Book, blank=True, related_name="discounts", verbose_name="کتاب‌های خاص")
    applicable_formats = models.ManyToManyField(BookFormat, blank=True, related_name="discounts", verbose_name="فرمت‌های خاص")
    applicable_genres = models.ManyToManyField(Genre, blank=True, related_name="discounts", verbose_name="ژانرهای خاص")
    applicable_authors = models.ManyToManyField(Author, blank=True, related_name="discounts", verbose_name="نویسندگان خاص")

    def __str__(self):
        if self.type == self.DiscountType.PERCENTAGE:
            return f"{self.code} ({self.value}%)"
        return f"{self.code} ({self.value} تومان)"

    def is_expired(self):
        return timezone.now() < self.start_date or timezone.now() > self.end_date

    def is_fully_used(self):
        if self.max_uses is None:
            return False
        return self.times_used >= self.max_uses

    def record_usage(self, user):
        """Records a new use of this discount for a specific user."""
        # Increment total uses
        self.times_used += 1

        # Record usage for the specific user
        usage, created = DiscountUsage.objects.get_or_create(discount=self, user=user)
        usage.use_count += 1
        usage.save()

        self.save()

class DiscountUsage(models.Model):
    """Tracks the usage of a discount by a specific user."""
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discount_usages")
    use_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('discount', 'user')
        verbose_name = "استفاده از تخفیف"
        verbose_name_plural = "استفاده از تخفیف‌ها"

    def __str__(self):
        return f"'{self.discount.code}' used by '{self.user.username}' {self.use_count} times"
