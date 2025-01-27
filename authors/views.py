from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Author
from .serializers import AuthorSerializer
from genres.models import Genre
from Language.models import Language

# ویو برای دریافت لیست نویسندگان
class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت شده دسترسی دارند

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # دریافت تمام نویسندگان
        if not queryset:
            return Response({"error": "No authors found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)  # سریالایزر برای نویسندگان
        return Response({"success": "Authors retrieved successfully.", "data": serializer.data})

# ویو برای دریافت جزئیات یک نویسنده بر اساس ID
class AuthorRetrieveView(generics.RetrieveAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت شده دسترسی دارند

    def retrieve(self, request, *args, **kwargs):
        try:
            author = self.get_object()  # دریافت نویسنده بر اساس ID
            serializer = self.get_serializer(author)  # سریالایزر برای نویسنده
            return Response({"success": "Author retrieved successfully.", "data": serializer.data})
        except Author.DoesNotExist:
            return Response({"error": "Author not found."}, status=status.HTTP_404_NOT_FOUND)

# ویو برای فیلتر نویسندگان بر اساس ژانر، زبان و نام
class AuthorFilterView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت شده دسترسی دارند

    def get_queryset(self):
        queryset = Author.objects.all()  # دریافت تمام نویسندگان

        # فیلتر بر اساس ژانر
        genre_ids = self.request.query_params.get('genre', None)
        if genre_ids:
            genre_ids = genre_ids.split(',')  # جدا کردن ژانرها با ',' و تبدیل به لیست
            queryset = queryset.filter(genres__id__in=genre_ids)

        # فیلتر بر اساس زبان
        language_ids = self.request.query_params.get('language', None)
        if language_ids:
            language_ids = language_ids.split(',')  # جدا کردن زبان‌ها و تبدیل به لیست
            queryset = queryset.filter(languages__id__in=language_ids)

        # جستجو بر اساس نام
        name_query = self.request.query_params.get('name', None)
        if name_query:
            queryset = queryset.filter(first_name__icontains=name_query) | queryset.filter(last_name__icontains=name_query)

        if not queryset:
            return Response({"error": "No authors found with the specified filters."}, status=status.HTTP_404_NOT_FOUND)

        return queryset

# ویو برای جستجوی نویسندگان بر اساس نام
class AuthorSearchView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت شده دسترسی دارند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')  # دریافت پارامتر جستجو
        if query:
            queryset = Author.objects.filter(first_name__icontains=query) | Author.objects.filter(last_name__icontains=query)
            if not queryset:
                return Response({"error": "No authors found with the provided name."}, status=status.HTTP_404_NOT_FOUND)
            return queryset
        return Author.objects.none()

# ویو برای ایجاد نویسنده جدید (فقط برای ادمین)
class AuthorCreateView(generics.CreateAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها می‌توانند نویسنده ایجاد کنند

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": f"Error creating author: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# ویو برای به‌روزرسانی اطلاعات نویسنده (فقط برای ادمین)
class AuthorUpdateView(generics.UpdateAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها می‌توانند نویسنده را به‌روزرسانی کنند

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Author.DoesNotExist:
            return Response({"error": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error updating author: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# ویو برای حذف نویسنده (فقط برای ادمین)
class AuthorDeleteView(generics.DestroyAPIView):
    queryset = Author.objects.all()  # دریافت تمام نویسندگان
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها می‌توانند نویسنده را حذف کنند

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Author.DoesNotExist:
            return Response({"error": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error deleting author: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
