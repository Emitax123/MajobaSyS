"""
Vistas de clientes para la API REST de MajobaSyS.
"""
import logging

from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsOwner
from manager.models import Client
from .serializers import ClientCreateUpdateSerializer, ClientSerializer

logger = logging.getLogger('api')


class ClientViewSet(ModelViewSet):
    """
    ViewSet CRUD para clientes del usuario autenticado.

    list:    GET    /api/v1/clients/
    create:  POST   /api/v1/clients/
    retrieve: GET   /api/v1/clients/{id}/
    update:  PUT    /api/v1/clients/{id}/
    partial_update: PATCH /api/v1/clients/{id}/
    destroy: DELETE /api/v1/clients/{id}/
    """
    permission_classes = [IsAuthenticated, IsOwner]
    search_fields = ['name', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Filtra clientes al usuario autenticado y anota conteo de proyectos."""
        return (
            Client.objects.filter(user=self.request.user)
            .annotate(projects_count=Count('projects'))
            .order_by('name')
        )

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action in ('create', 'update', 'partial_update'):
            return ClientCreateUpdateSerializer
        return ClientSerializer

    def perform_create(self, serializer):
        """Asigna el usuario autenticado al crear un cliente."""
        serializer.save(user=self.request.user)
        logger.info(
            f"Cliente '{serializer.instance.name}' creado vía API "
            f"por {self.request.user.username}"
        )

    def perform_destroy(self, instance):
        """Registra la eliminación antes de borrar."""
        logger.info(
            f"Cliente '{instance.name}' eliminado vía API "
            f"por {self.request.user.username}"
        )
        instance.delete()
