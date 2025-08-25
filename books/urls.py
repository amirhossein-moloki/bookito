from django.urls import path, include
from rest_framework_nested import routers
from .views import BookViewSet
from reviews.views import ReviewViewSet

# Using SimpleRouter to avoid the default API root view
router = routers.SimpleRouter()
router.register(r'', BookViewSet, basename='books')

# Create a nested router for reviews under books.
# The `lookup` argument ('book') will create a URL pattern like /books/<book_pk>/reviews/
# The 'book_pk' kwarg is what the ReviewViewSet is expecting to find the parent book.
reviews_router = routers.NestedSimpleRouter(router, r'', lookup='book')
reviews_router.register(r'reviews', ReviewViewSet, basename='book-reviews')

# Combine the urlpatterns from both the parent and the nested router.
urlpatterns = router.urls + reviews_router.urls
