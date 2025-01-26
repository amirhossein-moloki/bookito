from django.db import models

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)  # کد تخفیف
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # درصد تخفیف
    start_date = models.DateTimeField()  # تاریخ شروع تخفیف
    end_date = models.DateTimeField()  # تاریخ پایان تخفیف
    is_active = models.BooleanField(default=True)  # وضعیت فعال بودن تخفیف

    def __str__(self):
        return f'{self.code} - {self.percentage}%'
