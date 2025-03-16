from rest_framework import generics
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Publisher
from .serializers import PublisherSerializer

# نمایش لیست تمام انتشارات و ایجاد یک انتشارات جدید
class PublisherListCreateView(generics.ListCreateAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [AllowAny]  # مشاهده لیست برای همه کاربران آزاد است، ایجاد فقط برای ادمین‌ها

    def perform_create(self, serializer):
        serializer.save()  # ایجاد رکورد جدید

    def get(self, request, *args, **kwargs):
        publishers = self.get_queryset()
        if not publishers:
            return Response({"خطا": "هیچ انتشاراتی یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(publishers, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"خطا": "دسترسی غیرمجاز"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"خطا": "داده‌های نامعتبر", "جزئیات": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# نمایش، بروزرسانی و حذف یک انتشارات خاص
class PublisherRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به دسترسی هستند

    def get(self, request, *args, **kwargs):
        try:
            publisher = self.get_object()
            serializer = self.get_serializer(publisher)
            return Response(serializer.data)
        except Publisher.DoesNotExist:
            return Response({"خطا": "انتشارات یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        publisher = self.get_object()
        serializer = self.get_serializer(publisher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"پیام": "انتشارات با موفقیت بروزرسانی شد", "داده‌ها": serializer.data}, status=status.HTTP_200_OK)
        return Response({"خطا": "داده‌های نامعتبر", "جزئیات": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        publisher = self.get_object()
        publisher.delete()
        return Response({"پیام": "انتشارات با موفقیت حذف شد"}, status=status.HTTP_204_NO_CONTENT)

# جستجو بر اساس نام انتشارات
class PublisherSearchView(generics.ListAPIView):
    serializer_class = PublisherSerializer
    permission_classes = [AllowAny]  # جستجو برای همه کاربران آزاد است

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            return Publisher.objects.filter(name__icontains=query)
        return Publisher.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"خطا": "هیچ انتشاراتی مطابق با جستجو یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# نمایش جزئیات یک انتشارات
class PublisherRetrieveView(generics.RetrieveAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [AllowAny]  # مشاهده جزئیات برای همه کاربران آزاد است

    def get(self, request, *args, **kwargs):
        try:
            publisher = self.get_object()
            serializer = self.get_serializer(publisher)
            return Response(serializer.data)
        except Publisher.DoesNotExist:
            return Response({"خطا": "انتشارات یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
