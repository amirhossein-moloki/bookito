from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from books.models import Book, BookFormat
from .models import Cart, CartItem, Invoice, InvoiceItem, Customer

class PreOrderTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password'
        )
        self.client.login(username='testuser', password='password')

        self.book = Book.objects.create(title='Pre-order Book')
        self.book_format_preorder = BookFormat.objects.create(
            book=self.book,
            format_name='Hardcover',
            price=150,
            stock=0,
            status=BookFormat.Status.PRE_ORDER
        )
        self.customer = Customer.objects.create(user=self.user)

    def test_add_preorder_to_cart(self):
        response = self.client.post(reverse('customers:add_to_cart'), {'book_format_id': self.book_format_preorder.id, 'quantity': 1})
        self.assertEqual(response.status_code, 200)
        cart = Cart.objects.get(customer=self.customer)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().book_format, self.book_format_preorder)

    def test_create_invoice_with_preorder_item(self):
        # First, add the item to the cart
        self.client.post(reverse('customers:add_to_cart'), {'book_format_id': self.book_format_preorder.id, 'quantity': 1})

        # Simulate a successful payment and invoice creation
        cart = Cart.objects.get(customer=self.customer)
        invoice = Invoice.objects.create(
            customer=self.user,
            total_price=cart.total_price,
            paid=True
        )
        for item in cart.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                book_format=item.book_format,
                quantity=item.quantity,
                price=item.book_format.price,
                is_preorder=(item.book_format.status == BookFormat.Status.PRE_ORDER)
            )
        cart.clear()

        # Check the created invoice
        self.assertEqual(Invoice.objects.count(), 1)
        created_invoice = Invoice.objects.first()
        self.assertEqual(created_invoice.items.count(), 1)
        invoice_item = created_invoice.items.first()
        self.assertTrue(invoice_item.is_preorder)
