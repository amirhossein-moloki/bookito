from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Translator
from .serializers import TranslatorSerializer

# 1. Create Translator
class TranslatorCreateView(generics.CreateAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به ایجاد مترجم هستند

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": "Error creating translator", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 2. Update Translator
class TranslatorUpdateView(generics.UpdateAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به آپدیت مترجم هستند

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Translator.DoesNotExist:
            return Response({"error": "Translator not found", "detail": "The translator you are trying to update does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Error updating translator", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 3. Delete Translator
class TranslatorDeleteView(generics.DestroyAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به حذف مترجم هستند

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Translator.DoesNotExist:
            return Response({"error": "Translator not found", "detail": "The translator you are trying to delete does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Error deleting translator", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 4. Search Translator
class TranslatorSearchView(generics.ListAPIView):
    serializer_class = TranslatorSerializer
    permission_classes = [IsAuthenticated]  # احراز هویت برای جستجو ضروری است

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            queryset = Translator.objects.filter(first_name__icontains=query) | Translator.objects.filter(last_name__icontains=query)
            if not queryset:
                return Response({"error": "No translators found with the provided name", "detail": "Please check the spelling or try a different name."}, status=status.HTTP_404_NOT_FOUND)
            return queryset
        return Translator.objects.none()

# 5. List All Translators
class TranslatorListView(generics.ListAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAuthenticated]  # احراز هویت برای مشاهده لیست مترجمان ضروری است

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"error": "No translators found", "detail": "There are no translators available at the moment."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": "Translators retrieved successfully", "detail": "All translators data has been retrieved.", "data": serializer.data})

# 6. Retrieve One Translator
class TranslatorRetrieveView(generics.RetrieveAPIView):
    queryset = Translator.objects.all()
    serializer_class = TranslatorSerializer
    permission_classes = [IsAuthenticated]  # احراز هویت برای مشاهده اطلاعات یک مترجم ضروری است

    def retrieve(self, request, *args, **kwargs):
        try:
            translator = self.get_object()
            serializer = self.get_serializer(translator)
            return Response({"success": "Translator retrieved successfully", "detail": "The translator's data has been successfully retrieved.", "data": serializer.data})
        except Translator.DoesNotExist:
            return Response({"error": "Translator not found", "detail": "The translator you are looking for does not exist."}, status=status.HTTP_404_NOT_FOUND)
