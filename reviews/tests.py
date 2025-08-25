from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from books.models import Book, BookFormat
from accounts.models import User
from .models import Review

class ReviewAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        cls.user1 = User.objects.create_user(username='user1', password='password123')
        cls.user2 = User.objects.create_user(username='user2', password='password123')
        cls.book = Book.objects.create(title='Test Book for Reviews')
        BookFormat.objects.create(book=cls.book, format_name='Paperback', price=100)

        # Create a review to be used in update/delete/get tests
        cls.review = Review.objects.create(
            book=cls.book,
            user=cls.user1,
            rating=4,
            comment="This is a test review."
        )

        cls.list_create_url = f'/books/{cls.book.pk}/reviews/'
        cls.detail_url = f'/books/{cls.book.pk}/reviews/{cls.review.pk}/'

    def test_list_reviews_for_book(self):
        """Ensure any user can list reviews for a book."""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rating'], 4)

    def test_create_review_unauthenticated(self):
        """Ensure unauthenticated users cannot create a review."""
        data = {'rating': 5, 'comment': 'A new review.'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_authenticated(self):
        """Ensure authenticated users can create a review."""
        book2 = Book.objects.create(title='Another Book')
        BookFormat.objects.create(book=book2, format_name='Hardcover', price=200)
        url = f'/books/{book2.pk}/reviews/'

        self.client.force_authenticate(user=self.user2)
        data = {'rating': 5, 'comment': 'A new review.'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['user']['username'], 'user2')

    def test_create_duplicate_review_fails(self):
        """Ensure a user cannot review the same book twice."""
        self.client.force_authenticate(user=self.user1)
        data = {'rating': 1, 'comment': 'Trying to review again.'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_by_owner(self):
        """Ensure the owner of a review can update it."""
        self.client.force_authenticate(user=self.user1)
        data = {'rating': 5, 'comment': 'An updated review.'}
        response = self.client.patch(self.detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'An updated review.')

    def test_update_review_by_non_owner_fails(self):
        """Ensure a user cannot update a review they do not own."""
        self.client.force_authenticate(user=self.user2)
        data = {'rating': 1}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_by_owner(self):
        """Ensure the owner of a review can delete it."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_delete_review_by_non_owner_fails(self):
        """Ensure a user cannot delete a review they do not own."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())
