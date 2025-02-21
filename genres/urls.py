from django.urls import path
from .views import GenreListCreateView, GenreRetrieveUpdateDestroyView, GenreSearchView

urlpatterns = [
    path('', GenreListCreateView.as_view(), name='genre-list-create'),
    path('<int:pk>/', GenreRetrieveUpdateDestroyView.as_view(), name='genre-retrieve-update-destroy'),
    path('search/', GenreSearchView.as_view(), name='genre-search'),
]
