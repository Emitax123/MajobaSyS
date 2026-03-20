"""
Serializers de autenticación para la API REST de MajobaSyS.
"""
import logging

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from majobacore.utils.http import get_client_ip
from users.models import CustomUser
from manager.services import create_manager

logger = logging.getLogger('api')


class LoginSerializer(serializers.Serializer):
    """
    Serializer para el login de usuarios.
    Valida credenciales y retorna el usuario autenticado.
    """
    username = serializers.CharField(
        max_length=150,
        help_text='Nombre de usuario',
    )
    password = serializers.CharField(
        write_only=True,
        help_text='Contraseña',
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )

        ip = get_client_ip(self.context.get('request'))

        if user is None:
            logger.warning(f"Login API fallido | usuario={username} | ip={ip}")
            raise serializers.ValidationError(
                'Credenciales inválidas.',
                code='invalid_credentials',
            )

        if not user.is_active:
            logger.warning(f"Login API cuenta desactivada | usuario={username} | ip={ip}")
            raise serializers.ValidationError(
                'Esta cuenta está desactivada.',
                code='inactive_account',
            )

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    """
    Serializer para el registro de usuarios.
    Solo administradores pueden crear usuarios (consistente con la web).
    """
    username = serializers.CharField(
        max_length=150,
        help_text='Nombre de usuario único',
    )
    password = serializers.CharField(
        write_only=True,
        help_text='Contraseña (mínimo 12 caracteres)',
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text='Confirmar contraseña',
    )
    first_name = serializers.CharField(
        max_length=150,
        help_text='Nombre',
    )
    last_name = serializers.CharField(
        max_length=150,
        help_text='Apellido',
    )
    phone = serializers.CharField(
        max_length=20,
        help_text='Teléfono',
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text='Correo electrónico (opcional)',
    )
    profession = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text='Profesión (opcional)',
    )
    direction = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text='Dirección (opcional)',
    )

    def validate_username(self, value):
        """Verifica que el nombre de usuario sea único."""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Ya existe un usuario con este nombre de usuario.'
            )
        return value

    def validate(self, attrs):
        """Valida que las contraseñas coincidan y cumplan requisitos."""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError(
                {'password_confirm': 'Las contraseñas no coinciden.'}
            )

        # Ejecutar validadores de Django (longitud mínima, complejidad, etc.)
        validate_password(password)

        return attrs

    def create(self, validated_data):
        """Crea el usuario y su ManagerData asociado."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data,
        )

        # Crear ManagerData automáticamente
        create_manager(user)

        logger.info(f"Usuario '{user.username}' creado vía API")
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña del usuario autenticado.
    """
    old_password = serializers.CharField(
        write_only=True,
        help_text='Contraseña actual',
    )
    new_password = serializers.CharField(
        write_only=True,
        help_text='Nueva contraseña (mínimo 12 caracteres)',
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        help_text='Confirmar nueva contraseña',
    )

    def validate_old_password(self, value):
        """Verifica que la contraseña actual sea correcta."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'La contraseña actual es incorrecta.'
            )
        return value

    def validate(self, attrs):
        """Valida que las nuevas contraseñas coincidan y cumplan requisitos."""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Las contraseñas no coinciden.'}
            )

        # Ejecutar validadores de Django
        validate_password(new_password, self.context['request'].user)

        return attrs


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer de solo lectura para la respuesta de tokens JWT.
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """Retorna información básica del usuario."""
        user = obj.get('user')
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name(),
                'is_staff': user.is_staff,
            }
        return None
