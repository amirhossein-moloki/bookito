from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Book, BookFormat, StockNotification

User = get_user_model()

class StockNotificationTests(APITestCase):
    def setUp(self):
        """Set up data for the stock notification tests."""
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')
        self.book = Book.objects.create(title='Out of Stock Book')

        self.out_of_stock_format = BookFormat.objects.create(
            book=self.book, format_name='Hardcover', price=25.00, stock=0
        )
        self.in_stock_format = BookFormat.objects.create(
            book=self.book, format_name='Paperback', price=15.00, stock=10
        )

        self.subscribe_url = reverse('stock-notification-list')

    def test_subscribe_unauthenticated(self):
        """Ensure unauthenticated users cannot subscribe."""
        response = self.client.post(self.subscribe_url, {'book_format': self.out_of_stock_format.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_to_in_stock_item_fails(self):
        """Ensure users cannot subscribe to an item that is in stock."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscribe_url, {'book_format': self.in_stock_format.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("in stock", response.data['book_format'][0])

    def test_subscribe_to_out_of_stock_item_succeeds(self):
        """Ensure users can subscribe to an out-of-stock item."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscribe_url, {'book_format': self.out_of_stock_format.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            StockNotification.objects.filter(user=self.user, book_format=self.out_of_stock_format).exists()
        )

    def test_duplicate_subscription_fails(self):
        """Ensure a user cannot subscribe to the same item twice."""
        self.client.force_authenticate(user=self.user)
        # First subscription
        self.client.post(self.subscribe_url, {'book_format': self.out_of_stock_format.id})
        # Second attempt
        response = self.client.post(self.subscribe_url, {'book_format': self.out_of_stock_format.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already subscribed", response.data['book_format'][0])

    def test_list_subscriptions(self):
        """Ensure a user can list their active subscriptions."""
        self.client.force_authenticate(user=self.user)
        self.client.post(self.subscribe_url, {'book_format': self.out_of_stock_format.id})

        response = self.client.get(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.username)

    @patch('books.signals.send_mail')
    def test_notification_email_sent_on_restock(self, mock_send_mail):
        """Test that an email is sent when a product is restocked."""
        # User subscribes to notification
        StockNotification.objects.create(user=self.user, book_format=self.out_of_stock_format)

        # Update the stock
        self.out_of_stock_format.stock = 5
        self.out_of_stock_format.save()

        # Check that send_mail was called
        mock_send_mail.assert_called_once()

        # Check email content
        args, kwargs = mock_send_mail.call_args
        self.assertIn("کتاب مورد علاقه شما موجود شد", args[0])
        self.assertIn(self.user.username, args[1])
        self.assertEqual(args[3], [self.user.email])

        # Check that the notification is marked as notified
        notification = StockNotification.objects.get(user=self.user, book_format=self.out_of_stock_format)
        self.assertTrue(notification.notified)
        self.assertIsNotNone(notification.notified_at)

    @patch('books.signals.send_mail')
    def test_no_email_sent_if_stock_does_not_change_from_zero(self, mock_send_mail):
        """Test that no email is sent if stock is updated but remains zero or was already positive."""
        # Scenario 1: Stock was already positive
        self.in_stock_format.stock = 15
        self.in_stock_format.save()
        mock_send_mail.assert_not_called()

        # Scenario 2: Stock is updated but remains zero
        self.out_of_stock_format.stock = 0
        self.out_of_stock_format.save()
        mock_send_mail.assert_not_called()
