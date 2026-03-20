from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'', views.ProjectViewSet, basename='api_projects')

urlpatterns = router.urls
