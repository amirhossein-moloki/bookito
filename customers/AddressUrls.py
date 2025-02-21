from django.urls import path
from .AddressViews import AddressViewSet

address_list = AddressViewSet.as_view({
    'get': 'list',  # دریافت لیست آدرس‌ها
    'post': 'create',  # ایجاد آدرس جدید
})

address_detail = AddressViewSet.as_view({
    'get': 'retrieve',  # دریافت جزئیات یک آدرس
    'put': 'update',  # بروزرسانی کامل
    'patch': 'partial_update',  # بروزرسانی جزئی
    'delete': 'destroy',  # حذف آدرس
})

urlpatterns = [
    path('', address_list, name='address-list'),
    path('<int:pk>/', address_detail, name='address-detail'),
]
