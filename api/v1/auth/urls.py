from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='api_login'),
    path('logout/', views.LogoutView.as_view(), name='api_logout'),
    path('register/', views.RegisterView.as_view(), name='api_register'),
    path('refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('change-password/', views.ChangePasswordView.as_view(), name='api_change_password'),
]
