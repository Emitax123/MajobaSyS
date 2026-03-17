"""
Vistas de autenticación para la API REST de MajobaSyS.
"""
import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from api.permissions import IsStaffUser
from api.throttling import LoginRateThrottle
from manager.services import create_manager
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
)

logger = logging.getLogger('api')


class LoginView(APIView):
    """
    Endpoint de login. Retorna tokens JWT y datos básicos del usuario.

    POST /api/v1/auth/login/
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Asegurar que existe ManagerData
        if not hasattr(user, 'manager_user'):
            create_manager(user)

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)

        logger.info(f"Login API exitoso para usuario: {user.username}")

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'is_staff': user.is_staff,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    Endpoint de logout. Invalida el refresh token (blacklist).

    POST /api/v1/auth/logout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'detail': 'Se requiere el token de refresco.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"Logout API para usuario: {request.user.username}")
            return Response(
                {'detail': 'Sesión cerrada exitosamente.'},
                status=status.HTTP_200_OK,
            )
        except TokenError:
            return Response(
                {'detail': 'Token inválido o ya expirado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterView(APIView):
    """
    Endpoint de registro de usuarios. Solo accesible para staff.

    POST /api/v1/auth/register/
    """
    permission_classes = [IsAuthenticated, IsStaffUser]

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                'detail': f'Usuario {user.username} creado exitosamente.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name(),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ChangePasswordView(APIView):
    """
    Endpoint para cambiar la contraseña del usuario autenticado.

    PUT /api/v1/auth/change-password/
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        logger.info(f"Contraseña cambiada vía API para usuario: {user.username}")

        return Response(
            {'detail': 'Contraseña actualizada exitosamente.'},
            status=status.HTTP_200_OK,
        )
