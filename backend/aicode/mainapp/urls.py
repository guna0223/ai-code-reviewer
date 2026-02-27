from rest_framework.routers import DefaultRouter
from .views import CodeReviewViewSet, AnalyzeViewSet

router = DefaultRouter()
router.register(r'aicode', CodeReviewViewSet)
router.register(r'analyze', AnalyzeViewSet, basename='analyze')

urlpatterns = router.urls
