from django.urls import path
from .views import PublisherListCreateView, PublisherRetrieveUpdateDestroyView, PublisherSearchView

urlpatterns = [
    # لیست و ایجاد انتشارات جدید
    path('publishers/', PublisherListCreateView.as_view(), name='publisher-list-create'),

    # دریافت، بروزرسانی و حذف یک انتشارات خاص
    path('publishers/<int:pk>/', PublisherRetrieveUpdateDestroyView.as_view(), name='publisher-retrieve-update-destroy'),

    # جستجو بر اساس نام انتشارات
    path('publishers/search/', PublisherSearchView.as_view(), name='publisher-search'),
]
