from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Book
from .serializers import BookSerializer
from .filters import BookFilter


# 1. CreateBookView - ایجاد کتاب
class CreateBookView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        try:
            serializer.save()
            return Response({"message": "Book successfully created."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error creating book: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 2. UpdateBookView - آپدیت کتاب
class UpdateBookView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        try:
            serializer.save()
            return Response({"message": "Book successfully updated."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error updating book: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 3. DeleteBookView - حذف کتاب
class DeleteBookView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    def perform_destroy(self, instance):
        try:
            instance.delete()
            return Response({"message": "Book successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"Error deleting book: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 4. BookListView - نمایش فهرست کتاب‌ها
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        books = self.get_queryset()
        if not books.exists():
            return Response({"error": "No books found."}, status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)


# 5. BookSearchView - جستجو بر اساس نام کتاب
class BookSearchView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if not query:
            return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        books = Book.objects.filter(title__icontains=query)
        if not books.exists():
            return Response({"error": "No books found matching the query."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 6. BookFilterView - فیلتر کردن کتاب‌ها
class BookFilterView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        books = BookFilter(self.request.GET, queryset=Book.objects.all()).qs
        if not books.exists():
            return Response({"error": "No books found with the specified filters."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 7. BookDiscountView - نمایش کتاب‌ها با تخفیف
class BookDiscountView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        min_discount = self.request.query_params.get('min_discount', 0)
        max_discount = self.request.query_params.get('max_discount', 100)
        books = Book.objects.filter(discount__gte=min_discount, discount__lte=max_discount)
        if not books.exists():
            return Response({"error": "No books found with the specified discount range."},
                            status=status.HTTP_404_NOT_FOUND)
        return books


# 8. BookPriceAscView - نمایش کتاب‌ها از ارزان به گران
class BookPriceAscView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        books = Book.objects.all().order_by('price')
        if not books.exists():
            return Response({"error": "No books available."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 9. BookPriceDescView - نمایش کتاب‌ها از گران به ارزان
class BookPriceDescView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        books = Book.objects.all().order_by('-price')
        if not books.exists():
            return Response({"error": "No books available."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 10. BookDetailView - نمایش جزئیات یک کتاب خاص
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            book = self.get_object()
            return Response({"message": "Book details retrieved successfully.", "data": BookSerializer(book).data})
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
