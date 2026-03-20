"""
Servicios de lógica de negocio para la app manager.

Este módulo centraliza funciones reutilizables que encapsulan
lógica de negocio compartida entre vistas web y endpoints de API.
"""
import logging
from django.db.models import F
from .models import ManagerData, Notification

logger = logging.getLogger('manager')


def create_manager(user):
    """
    Crea o recupera un ManagerData asociado a un usuario.

    Args:
        user: Instancia de CustomUser.

    Returns:
        ManagerData | None: El perfil creado/existente, o None si hubo error.
    """
    try:
        manager_data, created = ManagerData.objects.get_or_create(user=user)
        return manager_data
    except Exception as e:
        logger.error(f"Error al crear ManagerData para {user.username}: {e}")
        return None


def create_notification(manager_info, notification_type, points, description=None):
    """
    Crea una notificación para el usuario e incrementa su contador.

    Args:
        manager_info: Instancia de ManagerData del usuario.
        notification_type (int): Tipo de notificación (1 = sumar puntos, 2 = gastar puntos).
        points (int): Cantidad de puntos involucrados.
        description (str | None): Descripción personalizada (opcional).

    Returns:
        Notification | None: La notificación creada, o None si hubo error.
    """
    try:
        if notification_type == 1:
            message = f"¡Felicitaciones! sumaste {points} puntos."
            if not description:
                description = "Se han añadido puntos a tu cuenta."
        elif notification_type == 2:
            message = f"Gastaste {points} puntos."
            if not description:
                description = "Se han restado puntos de tu cuenta."
        else:
            return None

        notification = Notification.objects.create(
            user=manager_info.user,
            message=message,
            description=description,
            is_read=False,
        )

        manager_info.notifications = F('notifications') + 1
        manager_info.save(update_fields=['notifications'])

        logger.info(f"Notificación creada para {manager_info.user.username}: {message}")
        return notification

    except Exception as e:
        logger.error(f"Error al crear notificación: {e}")
        return None
