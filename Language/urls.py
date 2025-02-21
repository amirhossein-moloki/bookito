from django.urls import path
from .views import LanguageListCreateAPIView, LanguageRetrieveUpdateDestroyAPIView, LanguageSearchAPIView,LanguageRetrieveAPIView

urlpatterns = [
    path('', LanguageListCreateAPIView.as_view(), name='language-list-create'),
    path('<int:pk>/', LanguageRetrieveUpdateDestroyAPIView.as_view(), name='language-retrieve-update-destroy'),
    path('search/', LanguageSearchAPIView.as_view(), name='language-search'),

    path('detail/<int:pk>/', LanguageRetrieveAPIView.as_view(), name='language-detail'),


]
