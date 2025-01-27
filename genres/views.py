# views.py
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Genre
from .serializers import GenreSerializer


# ایجاد و دریافت تمام ژانرها
class GenreListCreateView(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به دسترسی هستند

    def perform_create(self, serializer):
        try:
            serializer.save()  # ایجاد رکورد جدید
        except Exception as e:
            return Response({"error": f"Failed to create genre: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        try:
            genres = self.queryset.all()  # دریافت تمامی ژانرها
            if not genres:
                return Response({"message": "No genres found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(genres, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error retrieving genres: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Error creating genre: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)


# دریافت، بروزرسانی و حذف یک ژانر خاص
class GenreRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به دسترسی هستند

    def get(self, request, *args, **kwargs):
        try:
            genre = self.get_object()
            serializer = self.get_serializer(genre)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Genre.DoesNotExist:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error retrieving genre: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        try:
            genre = self.get_object()
            serializer = self.get_serializer(genre, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Genre updated successfully", "data": serializer.data},
                                status=status.HTTP_200_OK)
            return Response({"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)
        except Genre.DoesNotExist:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error updating genre: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            genre = self.get_object()
            genre.delete()
            return Response({"message": "Genre deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Genre.DoesNotExist:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error deleting genre: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# جستجو در ژانرها بر اساس نام
class GenreSearchView(generics.ListAPIView):
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به دسترسی هستند

    def get_queryset(self):
        query = self.request.query_params.get('query', '')  # دریافت پارامتر جستجو از URL
        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            genres = Genre.objects.filter(name__icontains=query)  # جستجو بر اساس نام
            if not genres.exists():
                return Response({"error": "No genres found matching the query"}, status=status.HTTP_404_NOT_FOUND)
            return genres
        except Exception as e:
            return Response({"error": f"Error searching genres: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
