"""
Serializers de notificaciones para la API REST de MajobaSyS.
"""
from rest_framework import serializers

from manager.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer de notificación con tiempo transcurrido computado.
    """
    time_elapsed = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'message',
            'description',
            'is_read',
            'time_elapsed',
            'created_at',
        ]
        read_only_fields = fields
