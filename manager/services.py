"""
Servicios de lógica de negocio para la app manager.

Este módulo centraliza funciones reutilizables que encapsulan
lógica de negocio compartida entre vistas web y endpoints de API.
"""
import logging

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
        if created:
            manager_data.save()
        return manager_data
    except Exception as e:
        logger.error(f"Error al crear ManagerData para {user.username}: {e}")
        return None


def create_notification(manager_info, type, points, description=None):
    """
    Crea una notificación para el usuario e incrementa su contador.

    Args:
        manager_info: Instancia de ManagerData del usuario.
        type (int): Tipo de notificación (1 = sumar puntos, 2 = gastar puntos).
        points (int): Cantidad de puntos involucrados.
        description (str | None): Descripción personalizada (opcional).

    Returns:
        Notification | None: La notificación creada, o None si hubo error.
    """
    try:
        if type == 1:
            message = f"¡Felicitaciones! sumaste {points} puntos."
            if not description:
                description = "Se han añadido puntos a tu cuenta."
        elif type == 2:
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

        manager_info.notifications += 1
        manager_info.save()

        logger.info(f"Notificación creada para {manager_info.user.username}: {message}")
        return notification

    except Exception as e:
        logger.error(f"Error al crear notificación: {e}")
        return None
