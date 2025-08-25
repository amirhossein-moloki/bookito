from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from books.models import Book, Genre, Author
from reviews.models import Review
from .models import BookRecommendation
from .logic import get_content_based_recommendations, get_collaborative_filtering_recommendations, get_hybrid_recommendations

User = get_user_model()

class RecommendationLogicTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')

        # Create genres and authors
        self.genre1 = Genre.objects.create(name='Fantasy')
        self.genre2 = Genre.objects.create(name='Sci-Fi')
        self.author1 = Author.objects.create(first_name='Author', last_name='A')
        self.author2 = Author.objects.create(first_name='Author', last_name='B')

        # Create books
        self.book1 = Book.objects.create(title='Book 1')
        self.book1.genres.add(self.genre1)
        self.book1.authors.add(self.author1)
        self.book2 = Book.objects.create(title='Book 2')
        self.book2.genres.add(self.genre1)
        self.book2.authors.add(self.author2)
        self.book3 = Book.objects.create(title='Book 3')
        self.book3.genres.add(self.genre2)
        self.book3.authors.add(self.author1)
        self.book4 = Book.objects.create(title='Book 4')
        self.book4.genres.add(self.genre2)
        self.book4.authors.add(self.author2)

        # Create reviews
        Review.objects.create(user=self.user1, book=self.book1, rating=5)
        Review.objects.create(user=self.user2, book=self.book1, rating=4)
        Review.objects.create(user=self.user2, book=self.book3, rating=5)
        Review.objects.create(user=self.user3, book=self.book2, rating=3)

    def test_content_based_recommendations(self):
        recommendations = get_content_based_recommendations(self.user1)
        self.assertIn(self.book2, recommendations)
        self.assertIn(self.book3, recommendations)
        self.assertNotIn(self.book1, recommendations)

    def test_collaborative_filtering_recommendations(self):
        recommendations = get_collaborative_filtering_recommendations(self.user1)
        self.assertIn(self.book3, recommendations)
        self.assertNotIn(self.book1, recommendations)

    def test_hybrid_recommendations(self):
        recommendations = get_hybrid_recommendations(self.user1)
        self.assertIn(self.book2, recommendations)
        self.assertIn(self.book3, recommendations)

class UpdateRecommendationsCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.book = Book.objects.create(title='Test Book')
        Review.objects.create(user=self.user, book=self.book, rating=5)

    def test_update_recommendations_command(self):
        call_command('update_recommendations')
        self.assertTrue(BookRecommendation.objects.filter(user=self.user).exists())
        recommendation = BookRecommendation.objects.get(user=self.user)
        self.assertGreater(recommendation.recommendations.count(), 0)

class BookRecommendationAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(title='Recommended Book')
        recommendation = BookRecommendation.objects.create(user=self.user)
        recommendation.recommendations.add(self.book)

    def test_get_recommendations_authenticated(self):
        response = self.client.get('/recommendations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['recommendations'][0]['title'], 'Recommended Book')

    def test_get_recommendations_unauthenticated(self):
        self.client.logout()
        response = self.client.get('/recommendations/')
        self.assertEqual(response.status_code, 401)
