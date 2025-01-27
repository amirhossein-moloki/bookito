# serializers.py
from rest_framework import serializers
from .models import Author
from Language.serializers import LanguageSerializer
from genres.serializers import GenreSerializer


class AuthorSerializer(serializers.ModelSerializer):
    # استفاده از سریالایزر برای فیلدهای Many-to-Many
    languages = LanguageSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = '__all__'  # همه فیلدهای مدل Author را سریال می‌کند
