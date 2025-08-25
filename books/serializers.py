from rest_framework import serializers
from django.db.models import Avg
from .models import Book, BookFormat
from authors.serializers import AuthorSerializer
from publishers.serializers import PublisherSerializer
from translators.serializers import TranslatorSerializer
from genres.serializers import GenreSerializer
from Language.serializers import LanguageSerializer

class BookFormatSerializer(serializers.ModelSerializer):
    """
    Serializer for the BookFormat model. This represents a specific, purchasable
    version of a book.
    """
    class Meta:
        model = BookFormat
        fields = [
            'id',
            'format_name',
            'price',
            'isbn',
            'page_count',
            'weight',
            'cover_image',
            'stock',
            'discount',
        ]

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the conceptual Book model. It now includes a nested list
    of all its available formats.
    """
    authors = AuthorSerializer(many=True, read_only=True)
    translators = TranslatorSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    language = LanguageSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    formats = BookFormatSerializer(many=True, read_only=True)  # Nested serializer

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'authors',
            'translators',
            'publisher',
            'publication_date',
            'summary',
            'genres',
            'language',
            'sold_count',
            'average_rating',
            'reviews_count',
            'formats',  # Replaced old fields with this nested list
        ]
        read_only_fields = ['id', 'sold_count', 'average_rating', 'reviews_count']

    def get_average_rating(self, obj):
        """
        Calculates the average rating from all associated reviews.
        """
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 2)
        return None

    def get_reviews_count(self, obj):
        """
        Counts the total number of reviews for the book.
        """
        return obj.reviews.count()
