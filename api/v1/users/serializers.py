"""
Serializers de usuarios para la API REST de MajobaSyS.
"""
from rest_framework import serializers

from users.models import CustomUser
from manager.models import ManagerData


class ManagerDataNestedSerializer(serializers.ModelSerializer):
    """
    Serializer anidado de ManagerData para incluir en el perfil de usuario.
    """
    progress_percentage = serializers.IntegerField(read_only=True)
    points_for_next_level = serializers.IntegerField(read_only=True)
    next_level_display = serializers.CharField(read_only=True)

    class Meta:
        model = ManagerData
        fields = [
            'points',
            'acc_level',
            'notifications',
            'progress_percentage',
            'points_for_next_level',
            'next_level_display',
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer básico de usuario (listados, referencias).
    """

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
        ]
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado de usuario con datos de ManagerData anidados.
    """
    manager_data = ManagerDataNestedSerializer(
        source='manager_user',
        read_only=True,
    )
    full_name = serializers.CharField(
        source='get_full_name',
        read_only=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'full_name',
            'first_name',
            'last_name',
            'email',
            'phone',
            'profession',
            'direction',
            'is_active',
            'is_staff',
            'created_at',
            'updated_at',
            'manager_data',
        ]
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar datos del perfil del usuario autenticado.
    """

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'profession',
            'direction',
        ]

    def validate_email(self, value):
        """Valida unicidad del email excluyendo al usuario actual."""
        if value:
            user = self.context['request'].user
            if (
                CustomUser.objects.filter(email=value)
                .exclude(pk=user.pk)
                .exists()
            ):
                raise serializers.ValidationError(
                    'Ya existe un usuario con este correo electrónico.'
                )
        return value
