from rest_framework import serializers
from django.db.models import Avg
from .models import Book
from authors.serializers import AuthorSerializer
from publishers.serializers import PublisherSerializer
from translators.serializers import TranslatorSerializer
from genres.serializers import GenreSerializer
from Language.serializers import LanguageSerializer

class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    translators = TranslatorSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    language = LanguageSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'authors',
            'translators',
            'publisher',
            'publication_date',
            'isbn',
            'price',
            'summary',
            'genres',
            'language',
            'page_count',
            'cover_type',
            'cover_image',
            'stock',
            'sold_count',
            'average_rating',
            'reviews_count',
            'discount',
            'weight',
        ]
        read_only_fields = ['id', 'sold_count', 'stock', 'average_rating', 'reviews_count']

    def get_average_rating(self, obj):
        """
        Calculates the average rating for the book.
        The 'reviews' related_name comes from the Review model's ForeignKey to Book.
        """
        # The .all() is not strictly necessary but can be explicit
        reviews = obj.reviews.all()
        if reviews.exists():
            # The aggregate function returns a dictionary, e.g., {'rating__avg': 4.33}
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 2)
        return None  # Return None if there are no reviews

    def get_reviews_count(self, obj):
        """
        Counts the number of reviews for the book.
        """
        return obj.reviews.count()

    def validate_isbn(self, value):
        if value and len(value) != 13:
            raise serializers.ValidationError("ISBN must be exactly 13 characters.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_discount(self, value):
        if value and (value < 0 or value > 100):
            raise serializers.ValidationError("Discount must be between 0 and 100.")
        return value
