from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    is_online = models.BooleanField(default=False, verbose_name="Online Status")
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name="Last Seen")
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name="Profile Picture",
        default='profile_pictures/default_profile_picture.jpg'
    )
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")
    otp = models.CharField(max_length=6, blank=True, null=True, verbose_name="One Time Password (OTP)")
    otp_expiration = models.DateTimeField(blank=True, null=True, verbose_name="OTP Expiration Time")
    custom_id = models.BigIntegerField(unique=True, editable=False, null=True, verbose_name="Custom ID")  # آیدی 11 رقمی

    def __str__(self):
        return self.username

    def is_otp_valid(self):
        """ بررسی اعتبار کد OTP """
        if self.otp and self.otp_expiration:
            return timezone.now() < self.otp_expiration
        return False

    def get_profile_picture(self):
        """ بازگرداندن عکس پروفایل یا عکس پیش‌فرض """
        if self.profile_picture:
            return self.profile_picture.url
        return '/media/profile_pictures/default_profile_picture.jpg'

    def save(self, *args, **kwargs):
        """ تنظیم آیدی سفارشی در هنگام ذخیره """
        if not self.custom_id:
            self.custom_id = self.get_next_id()
        super().save(*args, **kwargs)

    @staticmethod
    def get_next_id():
        """ تولید آیدی سفارشی 11 رقمی """
        last_user = User.objects.all().order_by('custom_id').last()
        if not last_user:
            return 10000000000  # مقدار شروع
        return last_user.custom_id + 1  # مقدار بعدی
