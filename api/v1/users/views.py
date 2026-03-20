"""
Vistas de usuarios para la API REST de MajobaSyS.
"""
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserDetailSerializer, UserUpdateSerializer

logger = logging.getLogger('api')


class ProfileView(APIView):
    """
    Perfil del usuario autenticado.

    GET  /api/v1/users/profile/ — Obtener perfil completo
    PUT  /api/v1/users/profile/ — Actualizar perfil completo
    PATCH /api/v1/users/profile/ — Actualizar perfil parcial
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna el perfil completo del usuario autenticado."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Actualiza todos los campos editables del perfil."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(f"Perfil actualizado vía API para usuario: {request.user.username}")

        # Retornar perfil completo actualizado
        return Response(
            UserDetailSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        """Actualiza parcialmente los campos del perfil."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(f"Perfil actualizado parcialmente vía API para usuario: {request.user.username}")

        return Response(
            UserDetailSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )
