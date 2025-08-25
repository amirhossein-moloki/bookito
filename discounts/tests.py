from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from books.models import Book, BookFormat
from customers.models import Cart, CartItem, Customer
from .models import Discount

class DiscountLogicTest(TestCase):
    def setUp(self):
        # Users
        self.user = User.objects.create_user(username='testuser', password='password')
        self.customer = Customer.objects.create(user=self.user)

        # Books and Formats
        self.book1 = Book.objects.create(title='Book 1')
        self.format1 = BookFormat.objects.create(book=self.book1, format_name='Hardcover', price=100, stock=10)

        self.book2 = Book.objects.create(title='Book 2')
        self.format2 = BookFormat.objects.create(book=self.book2, format_name='Paperback', price=50, stock=10)

        # Cart
        self.cart = Cart.objects.create(customer=self.customer)
        CartItem.objects.create(cart=self.cart, book_format=self.format1, quantity=1)
        CartItem.objects.create(cart=self.cart, book_format=self.format2, quantity=2)
        # Cart total is 100 + 2*50 = 200

    def test_percentage_discount(self):
        discount = Discount.objects.create(
            code='PERCENT10',
            type=Discount.DiscountType.PERCENTAGE,
            value=10,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=True
        )
        self.cart.discount = discount
        self.cart.save()

        # 10% of 200 is 20
        self.assertEqual(self.cart.get_discount_amount(self.user), Decimal('20.00'))
        self.assertEqual(self.cart.total_price, Decimal('180.00'))

    def test_fixed_amount_discount(self):
        discount = Discount.objects.create(
            code='FIXED50',
            type=Discount.DiscountType.FIXED_AMOUNT,
            value=50,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=True
        )
        self.cart.discount = discount
        self.cart.save()

        self.assertEqual(self.cart.get_discount_amount(self.user), Decimal('50.00'))
        self.assertEqual(self.cart.total_price, Decimal('150.00'))

    def test_min_purchase_not_met(self):
        discount = Discount.objects.create(
            code='MIN300',
            type=Discount.DiscountType.PERCENTAGE,
            value=10,
            min_purchase_amount=300,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=True
        )
        self.cart.discount = discount
        self.cart.save()

        # Cart total is 200, min purchase is 300, so discount is 0
        self.assertEqual(self.cart.get_discount_amount(self.user), 0)
        self.assertEqual(self.cart.total_price, Decimal('200.00'))

    def test_product_specific_discount(self):
        discount = Discount.objects.create(
            code='BOOK1ONLY',
            type=Discount.DiscountType.PERCENTAGE,
            value=20,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=True
        )
        discount.applicable_books.add(self.book1)
        self.cart.discount = discount
        self.cart.save()

        # Discount should only apply to book1's format (price 100)
        # 20% of 100 is 20
        self.assertEqual(self.cart.get_discount_amount(self.user), Decimal('20.00'))
        self.assertEqual(self.cart.total_price, Decimal('180.00'))

    def test_usage_limit(self):
        discount = Discount.objects.create(
            code='ONCEONLY',
            type=Discount.DiscountType.FIXED_AMOUNT,
            value=10,
            max_uses=1,
            times_used=1,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=True
        )
        self.cart.discount = discount
        self.cart.save()

        # Discount is fully used, should return 0
        self.assertEqual(self.cart.get_discount_amount(self.user), 0)

    def test_record_usage(self):
        discount = Discount.objects.create(
            code='RECORDME',
            type=Discount.DiscountType.FIXED_AMOUNT,
            value=10,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=True
        )

        discount.record_usage(self.user)
        discount.refresh_from_db()

        self.assertEqual(discount.times_used, 1)
        self.assertEqual(discount.usages.count(), 1)
        self.assertEqual(discount.usages.first().use_count, 1)

        discount.record_usage(self.user)
        discount.refresh_from_db()
        self.assertEqual(discount.times_used, 2)
        self.assertEqual(discount.usages.first().use_count, 2)
