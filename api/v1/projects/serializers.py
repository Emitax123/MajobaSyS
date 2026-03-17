"""
Serializers de proyectos para la API REST de MajobaSyS.
"""
import logging

from rest_framework import serializers

from manager.models import Client, Project

logger = logging.getLogger('api')


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para listado de proyectos.
    """
    client_name = serializers.CharField(
        source='client.name',
        read_only=True,
        default=None,
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'client_name',
            'location',
            'start_date',
            'end_date',
            'is_active',
        ]
        read_only_fields = fields


class ClientNestedSerializer(serializers.ModelSerializer):
    """Serializer anidado de cliente para el detalle de proyecto."""

    class Meta:
        model = Client
        fields = ['id', 'name', 'phone']
        read_only_fields = fields


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado de proyecto con cliente anidado.
    """
    client = ClientNestedSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'location',
            'start_date',
            'end_date',
            'is_active',
            'client',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar proyectos.
    Soporta creación inline de clientes.
    """
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.none(),
        required=False,
        allow_null=True,
        help_text='ID del cliente existente',
    )
    new_client_name = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        help_text='Nombre del nuevo cliente (creación inline)',
    )
    new_client_phone = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        help_text='Teléfono del nuevo cliente (creación inline)',
    )

    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'location',
            'start_date',
            'end_date',
            'is_active',
            'client',
            'new_client_name',
            'new_client_phone',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar el queryset de clientes al usuario autenticado
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['client'].queryset = Client.objects.filter(
                user=request.user,
            )

    def validate_client(self, value):
        """Valida que el cliente pertenezca al usuario autenticado."""
        if value is not None:
            request = self.context.get('request')
            if request and value.user != request.user:
                raise serializers.ValidationError(
                    'El cliente seleccionado no te pertenece.'
                )
        return value

    def validate(self, attrs):
        """Valida que se proporcione un cliente existente o uno nuevo."""
        client = attrs.get('client')
        new_client_name = (attrs.get('new_client_name') or '').strip()

        if not client and not new_client_name:
            raise serializers.ValidationError(
                {'client': 'Debes seleccionar un cliente existente o crear uno nuevo.'}
            )

        return attrs

    def create(self, validated_data):
        """Crea el proyecto con soporte para creación inline de clientes."""
        new_client_name = validated_data.pop('new_client_name', '').strip()
        new_client_phone = validated_data.pop('new_client_phone', '').strip()
        request = self.context['request']

        if new_client_name:
            client = Client.objects.create(
                name=new_client_name,
                phone=new_client_phone,
                user=request.user,
            )
            validated_data['client'] = client
            logger.info(
                f"Cliente '{client.name}' creado inline vía API "
                f"por {request.user.username}"
            )

        validated_data['user'] = request.user
        project = Project.objects.create(**validated_data)

        logger.info(
            f"Proyecto '{project.name}' creado vía API "
            f"por {request.user.username}"
        )
        return project

    def update(self, instance, validated_data):
        """Actualiza el proyecto (ignora campos de creación inline)."""
        validated_data.pop('new_client_name', None)
        validated_data.pop('new_client_phone', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        logger.info(
            f"Proyecto '{instance.name}' actualizado vía API "
            f"por {self.context['request'].user.username}"
        )
        return instance
