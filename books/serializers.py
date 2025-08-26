import urllib.parse
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
    share_links = serializers.SerializerMethodField()

    rank = serializers.FloatField(read_only=True)

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
            'share_links',
            'rank',
        ]
        read_only_fields = ['id', 'sold_count', 'average_rating', 'reviews_count', 'share_links', 'rank']

    def to_representation(self, instance):
        """
        Dynamically add the 'rank' field to the representation if it exists.
        """
        ret = super().to_representation(instance)

        # Check if the instance has the 'rank' attribute (from annotation)
        if hasattr(instance, 'rank'):
            ret['rank'] = round(instance.rank, 4)
        else:
            # If rank is not present, we can either remove it or set to None
            # Depending on desired API behavior. Let's remove it if not present.
            if 'rank' in ret:
                del ret['rank']

        return ret

    def get_share_links(self, obj):
        """
        Generates social media sharing links for the book.
        """
        # NOTE: The base URL is a placeholder. The frontend should replace
        # 'https://example.com' with its actual domain.
        book_url = f"https://example.com/books/{obj.id}"
        encoded_url = urllib.parse.quote(book_url)

        text = f"Check out this book: {obj.title}"
        encoded_text = urllib.parse.quote(text)

        return {
            'twitter': f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_text}",
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
            'whatsapp': f"https://api.whatsapp.com/send?text={encoded_text}%20{encoded_url}"
        }

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
