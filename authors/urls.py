from django.urls import path
from .views import AuthorListView, AuthorRetrieveView, AuthorFilterView, AuthorSearchView, AuthorCreateView, AuthorUpdateView, AuthorDeleteView

urlpatterns = [
    path('', AuthorListView.as_view(), name='author-list'),
    path('<int:pk>/', AuthorRetrieveView.as_view(), name='author-retrieve'),
    path('filter/', AuthorFilterView.as_view(), name='author-filter'),
    path('search/', AuthorSearchView.as_view(), name='author-search'),
    path('create/', AuthorCreateView.as_view(), name='author-create'),
    path('update/<int:pk>/', AuthorUpdateView.as_view(), name='author-update'),
    path('delete/<int:pk>/', AuthorDeleteView.as_view(), name='author-delete'),
]
