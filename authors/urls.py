from django.urls import path
from .views import AuthorListView, AuthorRetrieveView, AuthorFilterView, AuthorSearchView, AuthorCreateView, AuthorUpdateView, AuthorDeleteView

urlpatterns = [
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', AuthorRetrieveView.as_view(), name='author-retrieve'),
    path('authors/filter/', AuthorFilterView.as_view(), name='author-filter'),
    path('authors/search/', AuthorSearchView.as_view(), name='author-search'),
    path('authors/create/', AuthorCreateView.as_view(), name='author-create'),
    path('authors/update/<int:pk>/', AuthorUpdateView.as_view(), name='author-update'),
    path('authors/delete/<int:pk>/', AuthorDeleteView.as_view(), name='author-delete'),
]
