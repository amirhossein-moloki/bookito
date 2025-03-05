from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .models import Book
from .serializers import BookSerializer
from .filters import BookFilter


# 1. CreateBookView - ایجاد کتاب
class CreateBookView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین می‌تواند کتاب ایجاد کند

    def perform_create(self, serializer):
        try:
            serializer.save()
            return Response({"message": "کتاب با موفقیت ایجاد شد."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"خطا در ایجاد کتاب: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 2. UpdateBookView - به‌روزرسانی کتاب
class UpdateBookView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین می‌تواند کتاب را به‌روزرسانی کند

    def perform_update(self, serializer):
        try:
            serializer.save()
            return Response({"message": "کتاب با موفقیت به‌روزرسانی شد."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"خطا در به‌روزرسانی کتاب: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 3. DeleteBookView - حذف کتاب
class DeleteBookView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین می‌تواند کتاب را حذف کند

    def perform_destroy(self, instance):
        try:
            instance.delete()
            return Response({"message": "کتاب با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"خطا در حذف کتاب: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# 4. BookListView - نمایش لیست کتاب‌ها
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # دسترسی عمومی برای همه کاربران

    def get(self, request, *args, **kwargs):
        books = self.get_queryset()
        if not books.exists():
            return Response({"error": "هیچ کتابی یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)


# 5. BookSearchView - جستجو برای کتاب‌ها بر اساس نام
class BookSearchView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # دسترسی عمومی برای همه کاربران

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if not query:
            return Response({"error": "پارامتر جستجو ضروری است."}, status=status.HTTP_400_BAD_REQUEST)

        books = Book.objects.filter(title__icontains=query)
        if not books.exists():
            return Response({"error": "هیچ کتابی با این نام پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 6. BookFilterView - فیلتر کتاب‌ها بر اساس پارامترهای جستجو
class BookFilterView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # دسترسی عمومی برای همه کاربران

    def get_queryset(self):
        # استفاده از BookFilter برای فیلتر کردن کتاب‌ها
        filtered_books = BookFilter(self.request.GET, queryset=Book.objects.all()).qs
        if not filtered_books.exists():
            return Response({"error": "هیچ کتابی با فیلترهای مشخص شده پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
        return filtered_books


# 7. BookDiscountView - نمایش کتاب‌ها با تخفیف
class BookDiscountView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # دسترسی عمومی برای همه کاربران

    def get_queryset(self):
        min_discount = self.request.query_params.get('min_discount', 0)
        max_discount = self.request.query_params.get('max_discount', 100)
        books = Book.objects.filter(discount__gte=min_discount, discount__lte=max_discount)
        if not books.exists():
            return Response({"error": "هیچ کتابی با این بازه تخفیف پیدا نشد."},
                            status=status.HTTP_404_NOT_FOUND)
        return books


# 8. BookPriceAscView - نمایش کتاب‌ها از ارزان‌ترین به گران‌ترین
class BookPriceAscView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # دسترسی عمومی برای همه کاربران

    def get_queryset(self):
        books = Book.objects.all().order_by('price')
        if not books.exists():
            return Response({"error": "هیچ کتابی در دسترس نیست."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 9. BookPriceDescView - نمایش کتاب‌ها از گران‌ترین به ارزان‌ترین
class BookPriceDescView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # دسترسی عمومی برای همه کاربران

    def get_queryset(self):
        books = Book.objects.all().order_by('-price')
        if not books.exists():
            return Response({"error": "هیچ کتابی در دسترس نیست."}, status=status.HTTP_404_NOT_FOUND)
        return books


# 10. BookDetailView - نمایش جزئیات یک کتاب خاص
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # دسترسی عمومی برای همه کاربران

    def get(self, request, *args, **kwargs):
        try:
            book = self.get_object()
            return Response({
                "message": "جزئیات کتاب با موفقیت بازیابی شد.",
                "data": BookSerializer(book).data
            })
        except Book.DoesNotExist:
            return Response({"error": "کتاب پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)
