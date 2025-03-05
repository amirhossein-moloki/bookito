from django.db import models

class Address(models.Model):
    PROVINCE_CHOICES = [
        ("1", "محل دائمی سکونت | مالک هستم | بیش از دو سال در این مکان هستم"),
        ("2", "محل دائمی سکونت | مالک هستم | بیش از یکسال و کمتر از دو سال در این مکان هستم"),
        ("3", "محل دائمی سکونت | مالک هستم | بزودی تغییر مکان می دهم"),
        ("4", "محل دائمی سکونت | مستاجر هستم | بیش از یکسال در این مکان هستم"),
        ("5", "محل دائمی سکونت | مستاجر هستم | کمتر از یکسال در این مکان هستم"),
        ("6", "محل موقت سکونت | در ایران ساکن نیستم و ساکن کشور دیگری هستم"),
        ("7", "محل موقت سکونت | مالک هستم | ساکن شهر دیگری هستم"),
        ("8", "محل موقتی سکونت | نه مالک و نه مستاجر هستم | بزودی تغییر مکان می دهم"),
        ("9", "محل دائمی کار و تجارت | مالک یا مستاجر هستم | بتازگی در این مکان هستم )کمتر از دوماه("),
        ("10", "محل دائمی کار و تجارت | مالک هستم | بیش از یکسال در این مکان هستم"),
        ("11", "محل دائمی کار و تجارت | مالک هستم | کمتر از یکسال در این مکان هستم )بیش از دو ماه("),
        ("12", "محل دائمی کار و تجارت | مستاجر هستم | بیش از یکسال در این مکان هستم"),
        ("13", "محل دائمی کار و تجارت | مستاجر هستم | کمتر از یکسال در این مکان هستم )بیش از دو ماه(")
    ]

    residence_type = models.CharField(
        max_length=2,
        choices=PROVINCE_CHOICES,
        null=True,
        blank=True,
        default=None
    )
    province = models.CharField(max_length=100, null=True, blank=True)
    province_code = models.CharField(max_length=10, null=True, blank=True)  # اضافه شده
    city = models.CharField(max_length=100, null=True, blank=True)
    city_code = models.CharField(max_length=10, null=True, blank=True)  # اضافه شده
    street_address = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    unit_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.province}"