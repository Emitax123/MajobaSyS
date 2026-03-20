from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'', views.NotificationViewSet, basename='api_notifications')

urlpatterns = router.urls
