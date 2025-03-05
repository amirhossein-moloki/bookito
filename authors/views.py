from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Author
from .serializers import AuthorSerializer
from genres.models import Genre
from Language.models import Language

# ویو برای لیست نویسندگان
class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = []  # تمام کاربران می‌توانند به این ویو دسترسی داشته باشند

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # دریافت تمام نویسندگان
        if not queryset:
            return Response({"error": "هیچ نویسنده‌ای پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)  # سریالیز کردن نویسندگان
        return Response({"success": "نویسندگان با موفقیت دریافت شدند.", "data": serializer.data})

# ویو برای دریافت یک نویسنده با استفاده از ID
class AuthorRetrieveView(generics.RetrieveAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = []  # تمام کاربران می‌توانند به این ویو دسترسی داشته باشند

    def retrieve(self, request, *args, **kwargs):
        try:
            author = self.get_object()  # دریافت نویسنده بر اساس ID
            serializer = self.get_serializer(author)  # سریالیز کردن نویسنده
            return Response({"success": "نویسنده با موفقیت دریافت شد.", "data": serializer.data})
        except Author.DoesNotExist:
            return Response({"error": "نویسنده پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

# ویو برای فیلتر کردن نویسندگان بر اساس ژانر، زبان و نام
class AuthorFilterView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    permission_classes = []  # تمام کاربران می‌توانند به این ویو دسترسی داشته باشند

    def get_queryset(self):
        queryset = Author.objects.all()  # دریافت تمام نویسندگان

        # فیلتر بر اساس ژانر
        genre_ids = self.request.query_params.get('genre', None)
        if genre_ids:
            genre_ids = genre_ids.split(',')  # تقسیم ژانرها بر اساس ',' و تبدیل به لیست
            queryset = queryset.filter(genres__id__in=genre_ids)

        # فیلتر بر اساس زبان
        language_ids = self.request.query_params.get('language', None)
        if language_ids:
            language_ids = language_ids.split(',')  # تقسیم زبان‌ها بر اساس ',' و تبدیل به لیست
            queryset = queryset.filter(languages__id__in=language_ids)

        # جستجو بر اساس نام
        name_query = self.request.query_params.get('name', None)
        if name_query:
            queryset = queryset.filter(first_name__icontains=name_query) | queryset.filter(last_name__icontains=name_query)

        if not queryset:
            return Response({"error": "هیچ نویسنده‌ای با فیلترهای مشخص شده پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

        return queryset

# ویو برای جستجوی نویسندگان بر اساس نام
class AuthorSearchView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    permission_classes = []  # تمام کاربران می‌توانند به این ویو دسترسی داشته باشند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')  # دریافت پارامتر جستجو
        if query:
            queryset = Author.objects.filter(first_name__icontains=query) | Author.objects.filter(last_name__icontains=query)
            if not queryset:
                return Response({"error": "هیچ نویسنده‌ای با نام داده شده پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
            return queryset
        return Author.objects.none()

# ویو برای ایجاد نویسنده جدید (فقط برای ادمین‌ها)
class AuthorCreateView(generics.CreateAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها می‌توانند نویسنده ایجاد کنند

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": f"خطا در ایجاد نویسنده: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# ویو برای به‌روزرسانی جزئیات یک نویسنده (فقط برای ادمین‌ها)
class AuthorUpdateView(generics.UpdateAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها می‌توانند نویسنده را به‌روزرسانی کنند

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Author.DoesNotExist:
            return Response({"error": "نویسنده پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"خطا در به‌روزرسانی نویسنده: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# ویو برای حذف یک نویسنده (فقط برای ادمین‌ها)
class AuthorDeleteView(generics.DestroyAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها می‌توانند نویسنده را حذف کنند

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Author.DoesNotExist:
            return Response({"error": "نویسنده پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"خطا در حذف نویسنده: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
