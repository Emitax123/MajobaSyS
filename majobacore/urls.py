"""
URL configuration for majobacore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import (
    index, 
    majoba_view, 
    hormicons_view, 
    constructora_view, 
    budget_view,
    health_check,
    liveness_check,
    readiness_check,
)

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('manager/', include('manager.urls')),
    path('users/', include('users.urls')),
    
    # Páginas principales
    path('', index, name='index'),
    path('majoba/', majoba_view, name='majoba'),
    path('hormicons/', hormicons_view, name='hormicons'),
    path('constructora/', constructora_view, name='constructora'),
    path('budget/', budget_view, name='budget'),
    
    # Health check endpoints para Railway
    path('health/', health_check, name='health_check'),
    path('health/live/', liveness_check, name='liveness'),
    path('health/ready/', readiness_check, name='readiness'),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
