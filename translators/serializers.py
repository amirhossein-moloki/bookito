from rest_framework import serializers
from .models import Translator
from Language.serializers import LanguageSerializer
import datetime
class TranslatorSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(many=True)  # برای زبان‌هایی که مترجم به آن‌ها مسلط است
    profile_picture = serializers.ImageField(required=False)  # برای عکس پروفایل، اختیاری است
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)  # نمره مترجم

    class Meta:
        model = Translator
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'nationality', 'languages', 'biography', 'profile_picture', 'rating']

    def validate_rating(self, value):
        if value and (value < 0 or value > 10):
            raise serializers.ValidationError("Rating must be between 0 and 10.")
        return value

    def validate_birth_date(self, value):
        if value and value > datetime.date.today():
            raise serializers.ValidationError("Birth date cannot be in the future.")
        return value
