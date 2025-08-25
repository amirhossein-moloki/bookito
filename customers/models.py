from django.db import models
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

    def mark_as_paid(self):
        self.paid = True
        self.save()

    def get_items(self):
        return [item.get_item_details() for item in self.items.all()]

    def get_total_with_shipping(self):
        return self.total_price + self.shipping_cost

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    book_format = models.ForeignKey(BookFormat, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.book_format.book.title} ({self.book_format.format_name})"

    def get_item_details(self):
        return {
            "book_title": self.book_format.book.title,
            "format": self.book_format.format_name,
            "quantity": self.quantity,
            "price": self.price
        }

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

    def get_total_books_bought(self):
        return sum([item.quantity for item in InvoiceItem.objects.filter(invoice__customer=self.user)])

class CustomerInterest(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    genre_interest = models.JSONField(default=dict)
    author_interest = models.JSONField(default=dict)
    translator_interest = models.JSONField(default=dict)
    publisher_interest = models.JSONField(default=dict)

    def __str__(self):
        return f"Interest data for {self.customer.username}"

def update_customer_interest(customer, book_format, quantity=1):
    customer_interest, _ = CustomerInterest.objects.get_or_create(customer=customer)
    book = book_format.book

    for genre in book.genres.all():
        customer_interest.genre_interest[genre.name] = customer_interest.genre_interest.get(genre.name, 0) + quantity

    for author in book.authors.all():
        customer_interest.author_interest[author.full_name] = customer_interest.author_interest.get(author.full_name, 0) + quantity

    if book.publisher:
        customer_interest.publisher_interest[book.publisher.name] = customer_interest.publisher_interest.get(book.publisher.name, 0) + quantity

    for translator in book.translators.all():
        customer_interest.translator_interest[translator.full_name] = customer_interest.translator_interest.get(translator.full_name, 0) + quantity

    customer_interest.save()

class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    discount_code = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cart of {self.customer.full_name}"

    def get_total_price(self):
        total_price = sum([item.get_total_price() for item in self.items.all()])
        if self.discount_amount > 0:
            total_price -= self.discount_amount
        return total_price

    def get_total_items(self):
        return sum([item.quantity for item in self.items.all()])

    def get_total_weight(self):
        return sum([item.book_format.weight * item.quantity for item in self.items.all() if item.book_format.weight is not None])

    def get_total_price_without_discount(self):
        return sum([item.get_total_price() for item in self.items.all()])

    def clear_cart(self):
        self.items.all().delete()
        self.discount_code = None
        self.discount_amount = 0
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_format = models.ForeignKey(BookFormat, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book_format.book.title} ({self.book_format.format_name})"

    def get_total_price(self):
        return self.book_format.price * self.quantity
