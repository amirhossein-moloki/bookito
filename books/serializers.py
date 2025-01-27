from rest_framework import serializers
from models import  Book
from authors.serializers import AuthorSerializer
from publishers.serializers import PublisherSerializer
from translators.serializers import TranslatorSerializer
from genres.serializers import GenreSerializer
from Language.serializers import LanguageSerializer

class BookSerializer(serializers.serializerserializer):
    author = AuthorSerializer()  # استفاده از سریالایزر Author
    translator = TranslatorSerializer()  # استفاده از سریالایزر Translator
    publisher = PublisherSerializer()  # استفاده از سریالایزر Publisher
    genre = GenreSerializer()  # استفاده از سریالایزر Genre
    language = LanguageSerializer()  # استفاده از سریالایزر Language

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'translator',
            'publisher',
            'publication_date',
            'isbn',
            'price',
            'summary',
            'genre',
            'language',
            'page_count',
            'cover_image',
            'stock',
            'sold_count',
            'rating',
            'discount',
        ]
        read_only_fields = ['id', 'sold_count', 'rating', 'stock']  # فیلدهای فقط خواندنی

    def validate_isbn(self, value):
        if len(value) != 13:
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
