from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

from .models import Book
from .serializers import BookSerializer
from .filters import BookFilter

class BookViewSet(ModelViewSet):
    """
    A unified ViewSet for all actions related to Books.
    """
    queryset = Book.objects.all().prefetch_related('authors', 'translators', 'genres')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - Admin users are required for write actions (create, update, destroy).
        - Any user (including anonymous) can perform read actions.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    # --- Overriding default actions to keep custom responses ---

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "کتاب با موفقیت ایجاد شد.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "کتاب با موفقیت به‌روزرسانی شد.", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "کتاب با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"message": "جزئیات کتاب با موفقیت بازیابی شد.", "data": serializer.data})

    # --- Custom actions for specific queries ---

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Searches for books by title.
        Expects a 'query' query parameter.
        """
        query = request.query_params.get('query', None)
        if not query:
            return Response({"error": "پارامتر جستجو ضروری است."}, status=status.HTTP_400_BAD_REQUEST)

        books = self.get_queryset().filter(title__icontains=query)
        if not books.exists():
            return Response({"error": "هیچ کتابی با این نام پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='discount')
    def discount_list(self, request):
        """
        Lists books that have a discount.
        """
        books = self.get_queryset().filter(discount__isnull=False, discount__gt=0)
        if not books.exists():
            return Response({"error": "هیچ کتابی با تخفیف پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='price-asc')
    def price_asc(self, request):
        """
        Lists books ordered by price ascending.
        """
        books = self.get_queryset().order_by('price')
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='price-desc')
    def price_desc(self, request):
        """
        Lists books ordered by price descending.
        """
        books = self.get_queryset().order_by('-price')
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
