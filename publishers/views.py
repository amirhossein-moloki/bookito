from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Publisher
from .serializers import PublisherSerializer

# نمایش لیست تمام انتشارات و ایجاد یک انتشارات جدید
class PublisherListCreateView(generics.ListCreateAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به دسترسی هستند

    def perform_create(self, serializer):
        serializer.save()  # ایجاد رکورد جدید

    def get(self, request, *args, **kwargs):
        publishers = self.get_queryset()
        if not publishers:
            return Response({"error": "No publishers found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(publishers, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"error": "Publisher not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        publisher = self.get_object()
        serializer = self.get_serializer(publisher, data=request.data, partial=True)  # partial=True برای بروزرسانی جزئی
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Publisher updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        publisher = self.get_object()
        publisher.delete()
        return Response({"message": "Publisher deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# جستجو بر اساس نام انتشارات
class PublisherSearchView(generics.ListAPIView):
    serializer_class = PublisherSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به دسترسی هستند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')  # دریافت پارامتر جستجو از URL
        if query:
            return Publisher.objects.filter(name__icontains=query)  # جستجو بر اساس نام
        return Publisher.objects.none()  # اگر جستجو وجود نداشت، هیچ چیزی برنگرداند

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"error": "No publishers found matching the query"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
