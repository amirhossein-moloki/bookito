from django.urls import path
from .views import PublisherListCreateView, PublisherRetrieveUpdateDestroyView, PublisherSearchView

urlpatterns = [
    # لیست و ایجاد انتشارات جدید
    path('', PublisherListCreateView.as_view(), name='publisher-list-create'),

    # دریافت، بروزرسانی و حذف یک انتشارات خاص
    path('<int:pk>/', PublisherRetrieveUpdateDestroyView.as_view(), name='publisher-retrieve-update-destroy'),

    # جستجو بر اساس نام انتشارات
    path('search/', PublisherSearchView.as_view(), name='publisher-search'),
]
