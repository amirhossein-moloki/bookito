from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from books.models import Book, BookFormat
from .models import Cart, CartItem, Invoice, InvoiceItem, Customer, Wishlist
from rest_framework import status

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


class WishlistAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.customer = Customer.objects.create(user=self.user)

        self.book1 = Book.objects.create(title='Book 1')
        self.book_format1 = BookFormat.objects.create(book=self.book1, format_name='Paperback', price=100)

        self.book2 = Book.objects.create(title='Book 2')
        self.book_format2 = BookFormat.objects.create(book=self.book2, format_name='Hardcover', price=200)

        self.wishlist_list_create_url = reverse('customers:wishlist-list-create')

    def test_add_to_wishlist(self):
        response = self.client.post(self.wishlist_list_create_url, {'book_format_id': self.book_format1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Wishlist.objects.filter(customer=self.customer, book_format=self.book_format1).exists())

    def test_add_duplicate_to_wishlist(self):
        # Add the item once
        self.client.post(self.wishlist_list_create_url, {'book_format_id': self.book_format1.id})
        # Try to add it again
        response = self.client.post(self.wishlist_list_create_url, {'book_format_id': self.book_format1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_wishlist(self):
        # Add two items to the wishlist
        self.client.post(self.wishlist_list_create_url, {'book_format_id': self.book_format1.id})
        self.client.post(self.wishlist_list_create_url, {'book_format_id': self.book_format2.id})

        response = self.client.get(self.wishlist_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_remove_from_wishlist(self):
        # Add an item to the wishlist
        add_response = self.client.post(self.wishlist_list_create_url, {'book_format_id': self.book_format1.id})
        wishlist_item_id = add_response.data['id']

        # Remove the item
        remove_url = reverse('customers:wishlist-destroy', kwargs={'pk': wishlist_item_id})
        response = self.client.delete(remove_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Wishlist.objects.filter(id=wishlist_item_id).exists())

    def test_user_can_only_see_their_wishlist(self):
        # Create another user and their wishlist
        other_user = get_user_model().objects.create_user(username='otheruser', password='password')
        other_customer = Customer.objects.create(user=other_user)
        Wishlist.objects.create(customer=other_customer, book_format=self.book_format2)

        # Add an item to the current user's wishlist
        self.client.post(self.wishlist_list_create_url, {'book_format_id': self.book_format1.id})

        # Check that the current user only sees their own wishlist item
        response = self.client.get(self.wishlist_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['book_format']['id'], self.book_format1.id)

    def test_user_can_only_delete_from_their_wishlist(self):
        # Create another user and their wishlist item
        other_user = get_user_model().objects.create_user(username='otheruser', password='password')
        other_customer = Customer.objects.create(user=other_user)
        other_wishlist_item = Wishlist.objects.create(customer=other_customer, book_format=self.book_format2)

        # Try to delete the other user's wishlist item
        remove_url = reverse('customers:wishlist-destroy', kwargs={'pk': other_wishlist_item.id})
        response = self.client.delete(remove_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Wishlist.objects.filter(id=other_wishlist_item.id).exists())
