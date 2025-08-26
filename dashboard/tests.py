from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from customers.models import Invoice, Customer
from books.models import Book, BookFormat
import json

class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username='admin',
            password='password',
            email='admin@test.com'
        )
        self.client.login(username='admin', password='password')

        # Create some data for testing
        self.book = Book.objects.create(title='Test Book')
        self.book_format = BookFormat.objects.create(
            book=self.book,
            format_name='Hardcover',
            price=100
        )
        self.customer_user = get_user_model().objects.create_user(
            username='customer',
            password='password',
            email='customer@test.com'
        )
        self.customer = Customer.objects.create(user=self.customer_user)
        self.invoice = Invoice.objects.create(
            customer=self.customer_user,
            total_price=100,
            paid=True
        )

    def test_dashboard_view_loads_correctly(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard_view_context_data(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

        # Check for the presence of chart data in the context
        self.assertIn('sales_labels', response.context)
        self.assertIn('sales_values', response.context)
        self.assertIn('best_selling_books_labels', response.context)
        self.assertIn('best_selling_books_values', response.context)
        self.assertIn('new_customers_labels', response.context)
        self.assertIn('new_customers_values', response.context)

        # Check that the data is valid JSON
        try:
            json.loads(response.context['sales_labels'])
            json.loads(response.context['sales_values'])
        except json.JSONDecodeError:
            self.fail("sales_labels or sales_values is not valid JSON.")
