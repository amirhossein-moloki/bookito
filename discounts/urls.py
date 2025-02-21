from django.urls import path
from .views import (
    DiscountCreateView,
    DiscountUpdateView,
    DiscountDeleteView,
    DiscountListView,
    DiscountValidateView
)

urlpatterns = [
    path('create/', DiscountCreateView.as_view(), name='discount-create'),  # ایجاد تخفیف
    path('update/<int:pk>/', DiscountUpdateView.as_view(), name='discount-update'),  # ویرایش تخفیف
    path('delete/<int:pk>/', DiscountDeleteView.as_view(), name='discount-delete'),  # حذف تخفیف
    path('list/', DiscountListView.as_view(), name='discount-list'),  # مشاهده لیست تخفیف‌ها
    path('validate/', DiscountValidateView.as_view(), name='discount-validate'),  # بررسی اعتبار کد تخفیف
]
