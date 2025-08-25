from rest_framework import serializers
from django.db.models import Avg
from .models import Book, BookFormat, StockNotification
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


class StockNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a stock notification request.
    """
    user = serializers.StringRelatedField(read_only=True)
    book_format = serializers.PrimaryKeyRelatedField(
        queryset=BookFormat.objects.all(),
        write_only=True
    )

    class Meta:
        model = StockNotification
        fields = ['id', 'user', 'book_format', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_book_format(self, book_format):
        """
        Check that the book format is out of stock.
        """
        if book_format.stock > 0:
            raise serializers.ValidationError("Cannot subscribe to notifications for an item that is in stock.")

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if StockNotification.objects.filter(user=request.user, book_format=book_format, notified=False).exists():
                raise serializers.ValidationError("You have already subscribed for notifications for this item.")

        return book_format
