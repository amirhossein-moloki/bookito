from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
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
        if not publishers.exists():
            return Response({"error": "هیچ انتشاراتی یافت نشد", "detail": "در حال حاضر هیچ انتشاراتی در سیستم ثبت نشده است."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(publishers, many=True)
        return Response({"success": "لیست انتشارات دریافت شد", "data": serializer.data})

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "دسترسی غیرمجاز", "detail": "شما اجازه ایجاد انتشارات جدید را ندارید."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"success": "انتشارات جدید با موفقیت ایجاد شد", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": "داده‌های نامعتبر", "detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# نمایش، بروزرسانی و حذف یک انتشارات خاص
class PublisherRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به دسترسی هستند

    def get(self, request, *args, **kwargs):
        try:
            publisher = self.get_object()
            serializer = self.get_serializer(publisher)
            return Response({"success": "اطلاعات انتشارات دریافت شد", "data": serializer.data})
        except Publisher.DoesNotExist:
            return Response({"error": "انتشارات یافت نشد", "detail": "انتشارات موردنظر در سیستم وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        publisher = self.get_object()
        serializer = self.get_serializer(publisher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "انتشارات با موفقیت بروزرسانی شد", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "داده‌های نامعتبر", "detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            publisher = self.get_object()
            publisher.delete()
            return Response({"success": "انتشارات با موفقیت حذف شد"}, status=status.HTTP_204_NO_CONTENT)
        except Publisher.DoesNotExist:
            return Response({"error": "انتشارات یافت نشد", "detail": "انتشارات موردنظر برای حذف وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)

# جستجو بر اساس نام انتشارات
class PublisherSearchView(generics.ListAPIView):
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]  # جستجو برای کاربران احراز هویت شده آزاد است

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            queryset = Publisher.objects.filter(name__icontains=query)
            return queryset
        return Publisher.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error": "هیچ انتشاراتی مطابق با جستجو یافت نشد", "detail": "لطفاً نام دیگری را امتحان کنید."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": "نتایج جستجو دریافت شد", "data": serializer.data}, status=status.HTTP_200_OK)

# نمایش جزئیات یک انتشارات
class PublisherRetrieveView(generics.RetrieveAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]  # مشاهده جزئیات فقط برای کاربران احراز هویت شده آزاد است

    def get(self, request, *args, **kwargs):
        try:
            publisher = self.get_object()
            serializer = self.get_serializer(publisher)
            return Response({"success": "اطلاعات انتشارات دریافت شد", "data": serializer.data})
        except Publisher.DoesNotExist:
            return Response({"error": "انتشارات یافت نشد", "detail": "انتشارات موردنظر در سیستم وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)
