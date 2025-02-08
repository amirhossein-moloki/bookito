from rest_framework import serializers
from .models import Discount

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'code', 'percentage', 'start_date', 'end_date', 'is_active']

    def validate_percentage(self, value):
        # بررسی درصد تخفیف برای اینکه منفی نباشد
        if value < 0 or value > 100:
            raise serializers.ValidationError("درصد تخفیف باید بین ۰ تا ۱۰۰ باشد.")
        return value

    def validate(self, data):
        # بررسی تاریخ‌ها برای اینکه تاریخ شروع بعد از تاریخ پایان نباشد
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد.")
        return data
