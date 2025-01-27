from rest_framework import serializers
from .models import Language

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']  # مشخص می‌کنیم که کدام فیلدها باید در API نمایش داده بشن
