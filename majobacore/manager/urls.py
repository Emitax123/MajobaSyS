from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import manager_view, admin_dashboard_view, manager_modification, search_users_ajax

urlpatterns = [
    path('', manager_view, name='manager'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('modify/<int:user_id>/', manager_modification, name='manager_modification'),
    path('search-users/', search_users_ajax, name='search_users_ajax'),
]
