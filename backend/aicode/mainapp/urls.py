from rest_framework.routers import DefaultRouter
from .views import CodeReviewViewSet

router = DefaultRouter()
router.register(r'aicode', CodeReviewViewSet)

urlpatterns = router.urls