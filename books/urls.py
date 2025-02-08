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
    path('', BookListView.as_view(), name='book-list'),
    path('create/', CreateBookView.as_view(), name='create-book'),
    path('update/<int:pk>/', UpdateBookView.as_view(), name='update-book'),
    path('delete/<int:pk>/', DeleteBookView.as_view(), name='delete-book'),
    path('search/', BookSearchView.as_view(), name='search-book'),
    path('filter/', BookFilterView.as_view(), name='filter-books'),
    path('discount/', BookDiscountView.as_view(), name='books-with-discount'),
    path('price-asc/', BookPriceAscView.as_view(), name='books-price-asc'),
    path('price-desc/', BookPriceDescView.as_view(), name='books-price-desc'),
    path('detail/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]
