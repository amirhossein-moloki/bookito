from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Genre
from .serializers import GenreSerializer
from rest_framework.exceptions import PermissionDenied


# ایجاد و دریافت تمام ژانرها
class GenreListCreateView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]  # همه کاربران می‌توانند لیست را مشاهده کنند

    def perform_create(self, serializer):
        if not self.request.user.is_staff:  # فقط ادمین‌ها می‌توانند ژانر جدید ایجاد کنند
            raise PermissionDenied("شما اجازه ایجاد ژانر جدید را ندارید.")
        try:
            serializer.save()  # ایجاد رکورد جدید
        except Exception as e:
            return Response({"error": f"ایجاد ژانر با مشکل مواجه شد: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        try:
            genres = self.queryset.all()  # دریافت تمامی ژانرها
            if not genres:
                return Response({"message": "هیچ ژانری یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(genres, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"خطا در دریافت ژانرها: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_staff:  # فقط ادمین‌ها می‌توانند ژانر ایجاد کنند
            raise PermissionDenied("شما اجازه ایجاد ژانر جدید را ندارید.")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"خطا در ایجاد ژانر: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "داده‌های وارد شده معتبر نیستند"}, status=status.HTTP_400_BAD_REQUEST)


# دریافت، بروزرسانی و حذف یک ژانر خاص
class GenreRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها می‌توانند دسترسی به این ویو داشته باشند

    def get(self, request, *args, **kwargs):
        try:
            genre = self.get_object()  # دریافت ژانر خاص
            serializer = self.get_serializer(genre)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Genre.DoesNotExist:
            return Response({"error": "ژانر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"خطا در دریافت ژانر: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        try:
            genre = self.get_object()
            serializer = self.get_serializer(genre, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "ژانر با موفقیت به‌روزرسانی شد", "data": serializer.data},
                                status=status.HTTP_200_OK)
            return Response({"error": "داده‌های وارد شده معتبر نیستند"}, status=status.HTTP_400_BAD_REQUEST)
        except Genre.DoesNotExist:
            return Response({"error": "ژانر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"خطا در به‌روزرسانی ژانر: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            genre = self.get_object()
            genre.delete()
            return Response({"message": "ژانر با موفقیت حذف شد"}, status=status.HTTP_204_NO_CONTENT)
        except Genre.DoesNotExist:
            return Response({"error": "ژانر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"خطا در حذف ژانر: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# جستجو در ژانرها بر اساس نام
class GenreSearchView(generics.ListAPIView):
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]  # همه کاربران می‌توانند جستجو کنند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')  # دریافت پارامتر جستجو از URL
        if not query:
            return Response({"error": "پارامتر جستجو الزامی است"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            genres = Genre.objects.filter(name__icontains=query)  # جستجو بر اساس نام
            if not genres.exists():
                return Response({"error": "هیچ ژانری مطابق با جستجو پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)
            return genres
        except Exception as e:
            return Response({"error": f"خطا در جستجو در ژانرها: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# دریافت جزئیات یک ژانر
class GenreDetailView(generics.RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]  # همه کاربران می‌توانند جزئیات ژانر را مشاهده کنند

    def get(self, request, *args, **kwargs):
        try:
            genre = self.get_object()  # دریافت ژانر خاص
            serializer = self.get_serializer(genre)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Genre.DoesNotExist:
            return Response({"error": "ژانر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"خطا در دریافت جزئیات ژانر: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
