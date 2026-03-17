from django.urls import path, include

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('users/', include('api.v1.users.urls')),
    path('manager/', include('api.v1.manager.urls')),
    path('projects/', include('api.v1.projects.urls')),
    path('clients/', include('api.v1.clients.urls')),
    path('notifications/', include('api.v1.notifications.urls')),
]
