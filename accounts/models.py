from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$',
        message="Phone number must be entered in the format: '09123456789'."
    )
    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Phone Number"
    )

    # Make email optional
    email = models.EmailField(blank=True, null=True)

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
