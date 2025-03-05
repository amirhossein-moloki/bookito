from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .models import Book
from .serializers import BookSerializer
from .filters import BookFilter


# 1. CreateBookView - Create a book
class CreateBookView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]  # Only admin can create books

    def perform_create(self, serializer):
        try:
            serializer.save()
            return Response({"message": "Book successfully created."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error creating book: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 2. UpdateBookView - Update a book
class UpdateBookView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]  # Only admin can update books

    def perform_update(self, serializer):
        try:
            serializer.save()
            return Response({"message": "Book successfully updated."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error updating book: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 3. DeleteBookView - Delete a book
class DeleteBookView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]  # Only admin can delete books

    def perform_destroy(self, instance):
        try:
            instance.delete()
            return Response({"message": "Book successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"Error deleting book: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 4. BookListView - Display a list of books
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Public access for all users, authenticated or not

    def get(self, request, *args, **kwargs):
        books = self.get_queryset()
        if not books.exists():
            return Response({"error": "No books found."}, status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)


# 5. BookSearchView - Search for books by name
class BookSearchView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Public access for all users, authenticated or not

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if not query:
            return Response({"error": "Search parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        books = Book.objects.filter(title__icontains=query)
        if not books.exists():
            return Response({"error": "No books found matching the search."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 6. BookFilterView - Filter books based on query parameters
class BookFilterView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Public access for all users, authenticated or not

    def get_queryset(self):
        # Use BookFilter to filter books
        filtered_books = BookFilter(self.request.GET, queryset=Book.objects.all()).qs
        if not filtered_books.exists():
            return Response({"error": "No books found with the specified filters."}, status=status.HTTP_404_NOT_FOUND)
        return filtered_books


# 7. BookDiscountView - Display books with a discount
class BookDiscountView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Public access for all users, authenticated or not

    def get_queryset(self):
        min_discount = self.request.query_params.get('min_discount', 0)
        max_discount = self.request.query_params.get('max_discount', 100)
        books = Book.objects.filter(discount__gte=min_discount, discount__lte=max_discount)
        if not books.exists():
            return Response({"error": "No books found within the specified discount range."},
                            status=status.HTTP_404_NOT_FOUND)
        return books


# 8. BookPriceAscView - Display books from cheapest to most expensive
class BookPriceAscView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Public access for all users, authenticated or not

    def get_queryset(self):
        books = Book.objects.all().order_by('price')
        if not books.exists():
            return Response({"error": "No books available."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 9. BookPriceDescView - Display books from most expensive to cheapest
class BookPriceDescView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Public access for all users, authenticated or not

    def get_queryset(self):
        books = Book.objects.all().order_by('-price')
        if not books.exists():
            return Response({"error": "No books available."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 10. BookDetailView - Display details of a specific book
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Public access for all users, authenticated or not

    def get(self, request, *args, **kwargs):
        try:
            book = self.get_object()
            return Response({
                "message": "Book details successfully retrieved.",
                "data": BookSerializer(book).data
            })
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
