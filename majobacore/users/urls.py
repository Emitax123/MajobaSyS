from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import user_create_view, custom_login_view, custom_logout_view, profile_view, user_modification

urlpatterns = [
    path('create/', user_create_view, name='user_create'),
    path('login/', custom_login_view, name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('modify/<int:user_id>/', user_modification, name='user_modify'),
]
