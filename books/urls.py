from django.urls import path
from .views import (
    CreateBookView,
    UpdateBookView,
    DeleteBookView,
    BookListView,
    BookSearchView,
    BookFilterView,
    BookDiscountView,
    BookPriceAscView,
    BookPriceDescView,
    BookDetailView
)

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/create/', CreateBookView.as_view(), name='create-book'),
    path('books/update/<int:pk>/', UpdateBookView.as_view(), name='update-book'),
    path('books/delete/<int:pk>/', DeleteBookView.as_view(), name='delete-book'),
    path('books/search/', BookSearchView.as_view(), name='search-book'),
    path('books/filter/', BookFilterView.as_view(), name='filter-books'),
    path('books/discount/', BookDiscountView.as_view(), name='books-with-discount'),
    path('books/price-asc/', BookPriceAscView.as_view(), name='books-price-asc'),
    path('books/price-desc/', BookPriceDescView.as_view(), name='books-price-desc'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]
