from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Author
from .serializers import AuthorSerializer
from genres.models import Genre
from Language.models import Language

# View for listing authors
class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()  # Get all authors
    serializer_class = AuthorSerializer
    permission_classes = []  # All users can access this view

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # Get all authors
        if not queryset:
            return Response({"error": "No authors found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)  # Serialize authors
        return Response({"success": "Authors retrieved successfully.", "data": serializer.data})

# View for retrieving a single author by ID
class AuthorRetrieveView(generics.RetrieveAPIView):
    queryset = Author.objects.all()  # Get all authors
    serializer_class = AuthorSerializer
    permission_classes = []  # All users can access this view

    def retrieve(self, request, *args, **kwargs):
        try:
            author = self.get_object()  # Get author by ID
            serializer = self.get_serializer(author)  # Serialize the author
            return Response({"success": "Author retrieved successfully.", "data": serializer.data})
        except Author.DoesNotExist:
            return Response({"error": "Author not found."}, status=status.HTTP_404_NOT_FOUND)

# View for filtering authors by genre, language, and name
class AuthorFilterView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    permission_classes = []  # All users can access this view

    def get_queryset(self):
        queryset = Author.objects.all()  # Get all authors

        # Filter by genre
        genre_ids = self.request.query_params.get('genre', None)
        if genre_ids:
            genre_ids = genre_ids.split(',')  # Split genres by ',' and convert to list
            queryset = queryset.filter(genres__id__in=genre_ids)

        # Filter by language
        language_ids = self.request.query_params.get('language', None)
        if language_ids:
            language_ids = language_ids.split(',')  # Split languages by ',' and convert to list
            queryset = queryset.filter(languages__id__in=language_ids)

        # Search by name
        name_query = self.request.query_params.get('name', None)
        if name_query:
            queryset = queryset.filter(first_name__icontains=name_query) | queryset.filter(last_name__icontains=name_query)

        if not queryset:
            return Response({"error": "No authors found with the specified filters."}, status=status.HTTP_404_NOT_FOUND)

        return queryset

# View for searching authors by name
class AuthorSearchView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    permission_classes = []  # All users can access this view

    def get_queryset(self):
        query = self.request.query_params.get('query', '')  # Get search parameter
        if query:
            queryset = Author.objects.filter(first_name__icontains=query) | Author.objects.filter(last_name__icontains=query)
            if not queryset:
                return Response({"error": "No authors found with the provided name."}, status=status.HTTP_404_NOT_FOUND)
            return queryset
        return Author.objects.none()

# View for creating a new author (Only for admins)
class AuthorCreateView(generics.CreateAPIView):
    queryset = Author.objects.all()  # Get all authors
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # Only admins can create authors

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": f"Error creating author: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# View for updating an author's details (Only for admins)
class AuthorUpdateView(generics.UpdateAPIView):
    queryset = Author.objects.all()  # Get all authors
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # Only admins can update authors

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Author.DoesNotExist:
            return Response({"error": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error updating author: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# View for deleting an author (Only for admins)
class AuthorDeleteView(generics.DestroyAPIView):
    queryset = Author.objects.all()  # Get all authors
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # Only admins can delete authors

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Author.DoesNotExist:
            return Response({"error": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error deleting author: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
