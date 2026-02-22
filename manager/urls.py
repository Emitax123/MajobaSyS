from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import manager_view, admin_dashboard_view, manager_modification, search_users_ajax, create_project_view, list_projects_view, modify_project_view

urlpatterns = [
    path('', manager_view, name='manager'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('list-projects/', list_projects_view, name='list_projects'),
    path('modify-project/<int:project_id>/', modify_project_view, name='modify_project'),
    path('modify/<int:user_id>/', manager_modification, name='manager_modification'),
    path('search/', search_users_ajax, name='search'),  # Nueva URL para el JavaScript
    path('create-project/', create_project_view, name='create_project'),
]
