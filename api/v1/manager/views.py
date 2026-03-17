"""
Vistas del manager/dashboard para la API REST de MajobaSyS.
"""
import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from manager.models import ManagerData, Notification, Project
from manager.services import create_manager
from .serializers import DashboardSerializer, ManagerDataSerializer

logger = logging.getLogger('api')


class DashboardView(APIView):
    """
    Dashboard consolidado del usuario autenticado.

    GET /api/v1/manager/dashboard/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna datos consolidados para el dashboard."""
        user = request.user

        # Asegurar que existe ManagerData
        manager_data = getattr(user, 'manager_user', None)
        if manager_data is None:
            manager_data = create_manager(user)

        # Contar proyectos activos del usuario
        recent_projects_count = Project.objects.filter(
            user=user,
            is_active=True,
        ).count()

        # Contar notificaciones no leídas
        unread_notifications_count = Notification.objects.filter(
            user=user,
            is_read=False,
        ).count()

        data = {
            'user': user,
            'manager_data': manager_data,
            'recent_projects_count': recent_projects_count,
            'unread_notifications_count': unread_notifications_count,
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)


class ManagerDataDetailView(APIView):
    """
    Detalle del ManagerData del usuario autenticado.

    GET /api/v1/manager/data/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna el ManagerData del usuario autenticado."""
        manager_data = getattr(request.user, 'manager_user', None)
        if manager_data is None:
            manager_data = create_manager(request.user)

        if manager_data is None:
            return Response(
                {'detail': 'No se pudo obtener los datos del manager.'},
                status=500,
            )

        serializer = ManagerDataSerializer(manager_data)
        return Response(serializer.data)
