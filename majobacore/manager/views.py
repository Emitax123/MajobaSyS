from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ManagerData
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

def create_manager(user):
    """
    Función para crear un ManagerData asociado a un usuario.
    """
    try:
        manager_data, created = ManagerData.objects.get_or_create(user=user)
        if created:
            manager_data.save()
        return manager_data
    except Exception as e:
        logger.error(f"Error al crear ManagerData para {user.username}: {e}")
        return None

@login_required
def manager_view(request):
    """
    Vista principal del gestor de cuentas.
    Trae los datos para el management de la cuenta de este usuario
    """

    manager_info = ManagerData.objects.filter(user=request.user).first()

    return render(request, 'manager/account_manager.html', {'manager_info': manager_info})

def manager_staff_view(request):
    """
    Permite a un administrador ver y gestionar las cuentas de otros usuarios.
    Dentro de la vista, habra un campo de busqueda, donde el administrador, busca al user, 
    y luego puede editar sus datos de manager
    """
    try:
        query = request.GET.get('query')
        if query:
            manager_object = ManagerData.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)).first()
    except Exception as e:
        logger.error(f"Error al buscar ManagerData: {e}")
        manager_object = None
