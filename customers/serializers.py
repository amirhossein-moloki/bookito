from rest_framework import serializers
from .models import Invoice, InvoiceItem, Customer, CustomerInterest, Cart, CartItem
from books.serializers import BookSerializer
from authors.serializers import AuthorSerializer
from publishers.serializers import PublisherSerializer
from translators.serializers import TranslatorSerializer
from genres.serializers import GenreSerializer
from discounts.serializers import DiscountSerializer
from accounts.serializers import UserSerializer
from address.serializers import AddressSerializer

class InvoiceItemSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = InvoiceItem
        fields = ['book', 'quantity', 'price']


class InvoiceSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'customer', 'total_price', 'created_at', 'paid', 'items']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = AddressSerializer()
    favorite_genres = GenreSerializer(many=True)
    favorite_authors = AuthorSerializer(many=True)
    favorite_publishers = PublisherSerializer(many=True)
    favorite_translators = TranslatorSerializer(many=True)

    class Meta:
        model = Customer
        fields = ['user', 'full_name', 'phone_number', 'email', 'registration_date', 'is_active', 'address',
                  'favorite_genres', 'favorite_authors', 'favorite_publishers', 'favorite_translators']


class CustomerInterestSerializer(serializers.ModelSerializer):
    genre_interest = serializers.JSONField()
    author_interest = serializers.JSONField()
    translator_interest = serializers.JSONField()
    publisher_interest = serializers.JSONField()

    class Meta:
        model = CustomerInterest
        fields = ['customer', 'genre_interest', 'author_interest', 'translator_interest', 'publisher_interest']


class CartItemSerializer(serializers.ModelSerializer):
    book = BookSerializer()  # اطلاعات کتاب را به صورت تو در تویی سریال می‌کنیم
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['book', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return str(obj.get_total_price())  # نمایش قیمت کل به صورت رشته


class CartSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = CartItemSerializer(many=True)
    discount_code = DiscountSerializer()

    class Meta:
        model = Cart
        fields = ['customer', 'created_at', 'updated_at', 'is_active', 'discount_code', 'discount_amount', 'items']


