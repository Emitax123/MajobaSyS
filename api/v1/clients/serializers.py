"""
Serializers de clientes para la API REST de MajobaSyS.
"""
from rest_framework import serializers

from manager.models import Client


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer de cliente con conteo de proyectos asociados.
    """
    projects_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Client
        fields = [
            'id',
            'name',
            'phone',
            'created_at',
            'projects_count',
        ]
        read_only_fields = ['id', 'created_at', 'projects_count']


class ClientCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar clientes.
    """
    phone = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Client
        fields = ['name', 'phone']
