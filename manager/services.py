import logging
from .models import ManagerData

logger = logging.getLogger(__name__)


def create_manager(user):
    """
    Función para crear un ManagerData asociado a un usuario.
    """
    try:
        manager_data, _ = ManagerData.objects.get_or_create(user=user)
        return manager_data
    except Exception as e:
        logger.error(f"Error al crear ManagerData para {user.username}: {e}")
        return None
