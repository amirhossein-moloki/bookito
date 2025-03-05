from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Language
from .serializers import LanguageSerializer

# ویو برای ایجاد و لیست کردن زبان‌ها
class LanguageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]  # همه کاربران می‌توانند زبان‌ها را لیست کنند، اما فقط ادمین‌ها می‌توانند ایجاد کنند

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            serializer.save()  # فقط ادمین‌ها می‌توانند زبان ایجاد کنند
        else:
            raise PermissionDenied("You do not have permission to perform this action.")

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"پیام": "شما اجازه ایجاد زبان را ندارید"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"پیام": "لیست زبان‌ها دریافت شد", "داده‌ها": response.data}, status=response.status_code)


# ویو برای به‌روزرسانی، حذف و مشاهده زبان‌ها
class LanguageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # فقط ادمین‌ها می‌توانند زبان‌ها را مشاهده، به‌روزرسانی یا حذف کنند

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({"پیام": "اطلاعات زبان دریافت شد", "داده‌ها": response.data}, status=response.status_code)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"پیام": "شما اجازه به‌روزرسانی زبان را ندارید"}, status=status.HTTP_403_FORBIDDEN)
        response = super().update(request, *args, **kwargs)
        return Response({"پیام": "زبان با موفقیت به‌روزرسانی شد", "داده‌ها": response.data}, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"پیام": "شما اجازه حذف زبان را ندارید"}, status=status.HTTP_403_FORBIDDEN)
        super().destroy(request, *args, **kwargs)
        return Response({"پیام": "زبان با موفقیت حذف شد"}, status=status.HTTP_204_NO_CONTENT)


# ویو برای جستجو بر اساس نام زبان
class LanguageSearchAPIView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]  # همه کاربران می‌توانند جستجو کنند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            return Language.objects.filter(name__icontains=query)
        return Language.objects.none()  # در صورتی که پارامتر جستجو وجود نداشته باشد، هیچ زبانی برنگردانده می‌شود

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"پیام": "هیچ زبانی یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        response = super().list(request, *args, **kwargs)
        return Response({"پیام": "نتایج جستجو", "داده‌ها": response.data}, status=response.status_code)


# ویو برای مشاهده اطلاعات زبان‌ها
class LanguageRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]  # همه کاربران می‌توانند اطلاعات زبان‌ها را مشاهده کنند
    lookup_field = 'pk'  # استفاده از pk به عنوان شناسه برای جستجو
