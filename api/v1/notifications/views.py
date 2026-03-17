"""
Vistas de notificaciones para la API REST de MajobaSyS.
"""
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from manager.models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger('api')


class NotificationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet de notificaciones del usuario autenticado (solo lectura + acciones).

    list:      GET  /api/v1/notifications/
    retrieve:  GET  /api/v1/notifications/{id}/
    mark_read: POST /api/v1/notifications/{id}/mark-read/
    mark_all_read: POST /api/v1/notifications/mark-all-read/
    unread_count: GET /api/v1/notifications/unread-count/
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtra notificaciones al usuario autenticado, ordenadas por fecha."""
        return Notification.objects.filter(
            user=self.request.user,
        ).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Marca una notificación individual como leída."""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])

        logger.info(
            f"Notificación {notification.id} marcada como leída "
            f"por {request.user.username}"
        )
        return Response(
            {'detail': 'Notificación marcada como leída.'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Marca todas las notificaciones no leídas como leídas."""
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True)

        logger.info(
            f"{updated_count} notificaciones marcadas como leídas "
            f"por {request.user.username}"
        )
        return Response(
            {
                'detail': f'{updated_count} notificaciones marcadas como leídas.',
                'updated_count': updated_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """Retorna el conteo de notificaciones no leídas."""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()

        return Response(
            {'unread_count': count},
            status=status.HTTP_200_OK,
        )
