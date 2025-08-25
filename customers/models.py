from decimal import Decimal
from django.db import models
from django.db.models import F, Sum
from accounts.models import User
from books.models import Book, BookFormat
from discounts.models import Discount
from authors.models import Author
from publishers.models import Publisher
from translators.models import Translator
from genres.models import Genre
from Language.models import Language
from address.models import Address

class Invoice(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.id} for {self.customer.username}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    book_format = models.ForeignKey(BookFormat, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.book_format.book.title} ({self.book_format.format_name})"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.IntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Other')], null=True, blank=True)
    national_id = models.CharField(max_length=10, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL, related_name='customers')

    favorite_genres = models.ManyToManyField(Genre, blank=True, related_name='favorited_by')
    favorite_authors = models.ManyToManyField(Author, blank=True, related_name='favorited_by')
    favorite_publishers = models.ManyToManyField(Publisher, blank=True, related_name='favorited_by')
    favorite_translators = models.ManyToManyField(Translator, blank=True, related_name='favorited_by')

    def __str__(self):
        return f"{self.user.username}'s profile"

class CustomerInterest(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    genre_interest = models.JSONField(default=dict)
    author_interest = models.JSONField(default=dict)
    translator_interest = models.JSONField(default=dict)
    publisher_interest = models.JSONField(default=dict)

def update_customer_interest(customer, book_format, quantity=1):
    customer_interest, _ = CustomerInterest.objects.get_or_create(customer=customer)
    book = book_format.book
    # ... (rest of the logic)

class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def total_price_without_discount(self):
        return self.items.aggregate(total=Sum(F('quantity') * F('book_format__price')))['total'] or 0

    def get_discount_amount(self, user_for_check=None):
        if not self.discount or not self.discount.is_active or self.discount.is_expired() or self.discount.is_fully_used():
            return 0
        if self.discount.min_purchase_amount and self.total_price_without_discount < self.discount.min_purchase_amount:
            return 0
        if user_for_check and self.discount.max_uses_per_customer:
            usage = self.discount.usages.filter(user=user_for_check).first()
            if usage and usage.use_count >= self.discount.max_uses_per_customer:
                return 0
        is_global = not (self.discount.applicable_books.exists() or self.discount.applicable_formats.exists() or self.discount.applicable_genres.exists() or self.discount.applicable_authors.exists())
        eligible_price = 0
        if is_global:
            eligible_price = self.total_price_without_discount
        else:
            for item in self.items.all():
                book = item.book_format.book
                if (self.discount.applicable_books.filter(id=book.id).exists() or
                    self.discount.applicable_formats.filter(id=item.book_format.id).exists() or
                    self.discount.applicable_genres.filter(id__in=book.genres.values_list('id', flat=True)).exists() or
                    self.discount.applicable_authors.filter(id__in=book.authors.values_list('id', flat=True)).exists()):
                    eligible_price += item.get_total_price()
        if eligible_price == 0: return 0
        if self.discount.type == Discount.DiscountType.PERCENTAGE:
            amount = (self.discount.value / Decimal('100')) * eligible_price
        else:
            amount = self.discount.value
        return min(amount, eligible_price)

    @property
    def total_price(self):
        return self.total_price_without_discount - self.get_discount_amount(self.customer.user)

    def get_total_items(self):
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    def get_total_weight(self):
        return self.items.aggregate(total=Sum(F('quantity') * F('book_format__weight')))['total'] or 0

    def clear(self):
        self.items.all().delete()
        self.discount = None
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_format = models.ForeignKey(BookFormat, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.book_format.price * self.quantity
