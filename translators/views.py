from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from .models import Translator
from .serializers import TranslatorSerializer

# 1. ایجاد مترجم جدید (فقط برای ادمین‌ها)
class TranslatorCreateView(generics.CreateAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": "خطا در ایجاد مترجم", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 2. بروزرسانی مترجم (فقط برای ادمین‌ها)
class TranslatorUpdateView(generics.UpdateAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Translator.DoesNotExist:
            return Response({"error": "مترجم یافت نشد", "detail": "مترجمی که قصد بروزرسانی آن را دارید، وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "خطا در بروزرسانی مترجم", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 3. حذف مترجم (فقط برای ادمین‌ها)
class TranslatorDeleteView(generics.DestroyAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Translator.DoesNotExist:
            return Response({"error": "مترجم یافت نشد", "detail": "مترجمی که قصد حذف آن را دارید، وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "خطا در حذف مترجم", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 4. جستجوی مترجم (دسترسی عمومی)
class TranslatorSearchView(generics.ListAPIView):
    serializer_class = TranslatorSerializer
    permission_classes = [AllowAny]  # همه کاربران می‌توانند جستجو کنند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            queryset = Translator.objects.filter(first_name__icontains=query) | Translator.objects.filter(last_name__icontains=query)
            if not queryset:
                return Response({"error": "مترجمی با این نام یافت نشد", "detail": "لطفاً املای نام را بررسی کنید یا نام دیگری را امتحان کنید."}, status=status.HTTP_404_NOT_FOUND)
            return queryset
        return Translator.objects.none()

# 5. نمایش لیست تمامی مترجمان (دسترسی عمومی)
class TranslatorListView(generics.ListAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [AllowAny]  # همه کاربران می‌توانند لیست را ببینند

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"error": "هیچ مترجمی یافت نشد", "detail": "در حال حاضر هیچ مترجمی در سیستم وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": "لیست مترجمان با موفقیت دریافت شد", "detail": "تمامی اطلاعات مترجمان دریافت شد.", "data": serializer.data})

# 6. دریافت اطلاعات یک مترجم خاص (دسترسی عمومی)
class TranslatorRetrieveView(generics.RetrieveAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [AllowAny]  # همه کاربران می‌توانند اطلاعات یک مترجم را ببینند

    def retrieve(self, request, *args, **kwargs):
        try:
            translator = self.get_object()
            serializer = self.get_serializer(translator)
            return Response({"success": "اطلاعات مترجم با موفقیت دریافت شد", "detail": "اطلاعات این مترجم با موفقیت دریافت شد.", "data": serializer.data})
        except Translator.DoesNotExist:
            return Response({"error": "مترجم یافت نشد", "detail": "مترجمی که به دنبال آن هستید، وجود ندارد."}, status=status.HTTP_404_NOT_FOUND)
