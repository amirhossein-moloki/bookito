from rest_framework import serializers
from .models import BookRecommendation
from books.serializers import BookSerializer

class BookRecommendationSerializer(serializers.ModelSerializer):
    recommendations = BookSerializer(many=True, read_only=True)

    class Meta:
        model = BookRecommendation
        fields = ['recommendations', 'updated_at']
