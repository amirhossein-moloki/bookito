from django.urls import path
from .views import (
    TranslatorCreateView,
    TranslatorUpdateView,
    TranslatorDeleteView,
    TranslatorSearchView,
    TranslatorListView,
    TranslatorRetrieveView,
)

urlpatterns = [
    path('translator/create/', TranslatorCreateView.as_view(), name='translator-create'),  # ایجاد مترجم جدید
    path('translator/update/<int:pk>/', TranslatorUpdateView.as_view(), name='translator-update'),  # بروزرسانی مترجم
    path('translator/delete/<int:pk>/', TranslatorDeleteView.as_view(), name='translator-delete'),  # حذف مترجم
    path('translator/search/', TranslatorSearchView.as_view(), name='translator-search'),  # جستجوی مترجم
    path('translator/list/', TranslatorListView.as_view(), name='translator-list'),  # نمایش لیست مترجمان
    path('translator/<int:pk>/', TranslatorRetrieveView.as_view(), name='translator-retrieve'),  # دریافت اطلاعات یک مترجم
]
