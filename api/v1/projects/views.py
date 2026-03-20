"""
Vistas de proyectos para la API REST de MajobaSyS.
"""
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsOwner
from manager.models import Project
from .filters import ProjectFilter
from .serializers import (
    ProjectCreateUpdateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
)

logger = logging.getLogger('api')


class ProjectViewSet(ModelViewSet):
    """
    ViewSet CRUD para proyectos del usuario autenticado.

    list:    GET    /api/v1/projects/
    create:  POST   /api/v1/projects/
    retrieve: GET   /api/v1/projects/{id}/
    update:  PUT    /api/v1/projects/{id}/
    partial_update: PATCH /api/v1/projects/{id}/
    destroy: DELETE /api/v1/projects/{id}/
    """
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = ProjectFilter
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filtra proyectos al usuario autenticado."""
        return (
            Project.objects.filter(user=self.request.user)
            .select_related('client')
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectCreateUpdateSerializer

    def perform_destroy(self, instance):
        """Registra la eliminación antes de borrar."""
        logger.info(
            f"Proyecto '{instance.name}' eliminado vía API "
            f"por {self.request.user.username}"
        )
        instance.delete()
