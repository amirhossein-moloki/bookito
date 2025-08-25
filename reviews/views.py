from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Review
from .serializers import ReviewSerializer
from books.models import Book
from .permissions import IsOwnerOrReadOnly


class ReviewViewSet(ModelViewSet):
    """
    A ViewSet for viewing and editing reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        This view should return a list of all the reviews
        for the book as determined by the book_pk portion of the URL.
        """
        book_pk = self.kwargs.get('book_pk')
        if not book_pk:
            # This can be handled differently, e.g., return all reviews
            # or raise an error. Returning an empty queryset is safe.
            return Review.objects.none()

        book = get_object_or_404(Book, pk=book_pk)
        return Review.objects.filter(book=book)

    def perform_create(self, serializer):
        """
        Associate the review with the book from the URL and the logged-in user.
        Also, prevent duplicate reviews.
        """
        book_pk = self.kwargs.get('book_pk')
        book = get_object_or_404(Book, pk=book_pk)

        # Check for duplicate reviews by the same user for the same book
        if Review.objects.filter(book=book, user=self.request.user).exists():
            raise ValidationError("شما قبلاً برای این کتاب نظری ثبت کرده‌اید.")

        serializer.save(user=self.request.user, book=book)

    def perform_update(self, serializer):
        # The user and book should not be changed on update.
        # The IsOwnerOrReadOnly permission already ensures the user is correct.
        serializer.save()

    def perform_destroy(self, instance):
        # The IsOwnerOrReadOnly permission ensures the user is correct.
        instance.delete()
