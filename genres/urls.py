from django.urls import path
from .views import GenreListCreateView, GenreRetrieveUpdateDestroyView, GenreSearchView

urlpatterns = [
    path('genres/', GenreListCreateView.as_view(), name='genre-list-create'),
    path('genres/<int:pk>/', GenreRetrieveUpdateDestroyView.as_view(), name='genre-retrieve-update-destroy'),
    path('genres/search/', GenreSearchView.as_view(), name='genre-search'),
]
