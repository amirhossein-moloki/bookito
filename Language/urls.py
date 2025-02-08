from django.urls import path
from .views import LanguageListCreateAPIView, LanguageRetrieveUpdateDestroyAPIView, LanguageSearchAPIView,LanguageRetrieveAPIView

urlpatterns = [
    path('languages/', LanguageListCreateAPIView.as_view(), name='language-list-create'),
    path('languages/<int:pk>/', LanguageRetrieveUpdateDestroyAPIView.as_view(), name='language-retrieve-update-destroy'),
    path('languages/search/', LanguageSearchAPIView.as_view(), name='language-search'),

    path('languages/detail/<int:pk>/', LanguageRetrieveAPIView.as_view(), name='language-detail'),


]
