from rest_framework import serializers
from .models import Book
from authors.serializers import AuthorSerializer
from publishers.serializers import PublisherSerializer
from translators.serializers import TranslatorSerializer
from genres.serializers import GenreSerializer
from Language.serializers import LanguageSerializer

class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)  # استفاده از authors به‌صورت لیست
    translators = TranslatorSerializer(many=True)  # استفاده از translators به‌صورت لیست
    publisher = PublisherSerializer()  # نگه داشتن publisher به‌صورت تک‌مقداری
    genres = GenreSerializer(many=True)  # استفاده از genres به‌صورت لیست
    language = LanguageSerializer()  # استفاده از language به‌صورت تک‌مقداری

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
            'rating',
            'discount',
            'weight',  # اضافه کردن وزن کتاب
        ]
        read_only_fields = ['id', 'sold_count', 'rating', 'stock']

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
