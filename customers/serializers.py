from rest_framework import serializers
from .models import Invoice, InvoiceItem, Customer, CustomerInterest, Cart, CartItem, Wishlist
from books.serializers import BookFormatSerializer  # Updated import
from authors.serializers import AuthorSerializer
from publishers.serializers import PublisherSerializer
from translators.serializers import TranslatorSerializer
from genres.serializers import GenreSerializer
from discounts.serializers import DiscountSerializer
from accounts.serializers import UserSerializer
from address.serializers import AddressSerializer

class InvoiceItemSerializer(serializers.ModelSerializer):
    book_format = BookFormatSerializer(read_only=True)  # Changed field

    class Meta:
        model = InvoiceItem
        fields = ['id', 'book_format', 'quantity', 'price']  # Changed field


class InvoiceSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'customer', 'total_price', 'created_at', 'paid', 'items']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    favorite_genres = GenreSerializer(many=True, read_only=True)
    favorite_authors = AuthorSerializer(many=True, read_only=True)
    favorite_publishers = PublisherSerializer(many=True, read_only=True)
    favorite_translators = TranslatorSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['user', 'full_name', 'phone_number', 'email', 'registration_date', 'is_active', 'address',
                  'favorite_genres', 'favorite_authors', 'favorite_publishers', 'favorite_translators']


class CustomerInterestSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    genre_interest = serializers.JSONField(read_only=True)
    author_interest = serializers.JSONField(read_only=True)
    translator_interest = serializers.JSONField(read_only=True)
    publisher_interest = serializers.JSONField(read_only=True)

    class Meta:
        model = CustomerInterest
        fields = ['customer', 'genre_interest', 'author_interest', 'translator_interest', 'publisher_interest']


class CartItemSerializer(serializers.ModelSerializer):
    book_format = BookFormatSerializer(read_only=True)  # For displaying the nested object
    book_format_id = serializers.IntegerField(write_only=True)  # For creating/updating
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'book_format', 'book_format_id', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()


class WishlistSerializer(serializers.ModelSerializer):
    book_format = BookFormatSerializer(read_only=True)
    book_format_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'book_format', 'book_format_id', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    discount_code = DiscountSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'created_at', 'updated_at', 'is_active', 'discount_code',
                  'discount_amount', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()
