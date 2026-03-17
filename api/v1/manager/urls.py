from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='api_dashboard'),
    path('data/', views.ManagerDataDetailView.as_view(), name='api_manager_data'),
]
