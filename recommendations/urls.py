from rest_framework.routers import DefaultRouter
from .views import BookRecommendationViewSet

router = DefaultRouter()
router.register(r'', BookRecommendationViewSet, basename='recommendations')

urlpatterns = router.urls
