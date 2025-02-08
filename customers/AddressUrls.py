from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .AddressViews import AddressViewSet

# ایجاد یک router برای مدیریت آدرس‌ها
router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
]
