from rest_framework import viewsets, permissions
from .models import BookRecommendation
from .serializers import BookRecommendationSerializer

class BookRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BookRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return the book recommendations for the currently
        authenticated user.
        """
        user = self.request.user
        return BookRecommendation.objects.filter(user=user)
