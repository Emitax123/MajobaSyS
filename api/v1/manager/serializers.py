"""
Serializers del manager/dashboard para la API REST de MajobaSyS.
"""
from rest_framework import serializers

from manager.models import ManagerData
from api.v1.users.serializers import ManagerDataNestedSerializer


class ManagerDataSerializer(serializers.ModelSerializer):
    """
    Serializer completo de ManagerData con propiedades computadas.
    """
    progress_percentage = serializers.IntegerField(read_only=True)
    points_for_next_level = serializers.IntegerField(read_only=True)
    next_level_display = serializers.CharField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ManagerData
        fields = [
            'id',
            'username',
            'points',
            'acc_level',
            'notifications',
            'progress_percentage',
            'points_for_next_level',
            'next_level_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class DashboardSerializer(serializers.Serializer):
    """
    Serializer para el dashboard consolidado del usuario.
    Combina datos del usuario, ManagerData, proyectos y notificaciones.
    """
    user = serializers.SerializerMethodField()
    manager_data = serializers.SerializerMethodField()
    recent_projects_count = serializers.IntegerField(read_only=True)
    unread_notifications_count = serializers.IntegerField(read_only=True)

    def get_user(self, obj):
        """Retorna datos básicos del usuario."""
        user = obj['user']
        return {
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'is_staff': user.is_staff,
        }

    def get_manager_data(self, obj):
        """Retorna datos del ManagerData."""
        manager = obj.get('manager_data')
        if manager:
            return ManagerDataNestedSerializer(manager).data
        return None
