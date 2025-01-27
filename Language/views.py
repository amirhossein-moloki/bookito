from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Language
from .serializers import LanguageSerializer


# ویو برای ایجاد و لیست کردن زبان‌ها
class LanguageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # فقط ادمین‌ها می‌توانند زبان‌ها را ایجاد یا لیست کنند

    def create(self, request, *args, **kwargs):
        # استفاده از متد create برای ایجاد زبان جدید
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # استفاده از متد list برای بازگرداندن لیست زبان‌ها
        return super().list(request, *args, **kwargs)


# ویو برای به‌روزرسانی، حذف و مشاهده زبان‌ها
class LanguageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # فقط ادمین‌ها می‌توانند زبان‌ها را مشاهده، به‌روزرسانی یا حذف کنند

    def retrieve(self, request, *args, **kwargs):
        # استفاده از متد retrieve برای مشاهده جزئیات زبان
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # استفاده از متد update برای به‌روزرسانی زبان
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # استفاده از متد destroy برای حذف زبان
        return super().destroy(request, *args, **kwargs)


# ویو برای جستجو بر اساس نام زبان
class LanguageSearchAPIView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # فقط ادمین‌ها می‌توانند جستجو کنند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            return Language.objects.filter(name__icontains=query)
        return Language.objects.none()  # در صورتی که پارامتر جستجو وجود نداشته باشد، هیچ زبانی برنگردانده می‌شود
