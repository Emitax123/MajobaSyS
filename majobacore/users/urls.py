from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import user_create_view

urlpatterns = [
    path('create/', user_create_view, name='user_create'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
