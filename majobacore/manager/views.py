from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ManagerData
from .forms import ManagerDataForm
from users.models import CustomUser
from django.db import models
from django.shortcuts import redirect
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
    Esta vista permite al usuario ver y administrar la información del ManagerData asociado a su cuenta.
    """
    try:
        # Obtener o crear ManagerData para el usuario autenticado
        manager_info, created = ManagerData.objects.get_or_create(
            user=request.user,
            defaults={
                'points': 0,
                'acc_level': 'bronze',
                'notifications': 0
            }
        )
        
        if created:
            logger.info(f"ManagerData creado para el usuario {request.user.username}")
        
        return render(request, 'manager/account_manager.html', {
            'manager_info': manager_info,
            'user': request.user
        })
    except Exception as e:
        logger.error(f"Error al cargar ManagerData para {request.user.username}: {e}")
        return render(request, 'manager/account_manager.html', {
            'error': 'Error al cargar la información del manager.'
        })


@login_required
def admin_dashboard_view(request):
    """
    Dashboard especial para usuarios staff/administradores
    """
    if not request.user.is_staff:
        logger.warning(f"Usuario no-staff {request.user.username} intentó acceder al dashboard admin")
        return redirect('manager')
    
    try:
        # Estadísticas generales
        total_users = CustomUser.objects.count()
        staff_users = CustomUser.objects.filter(is_staff=True).count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        
        # Estadísticas de ManagerData
        total_managers = ManagerData.objects.count()
        total_points = ManagerData.objects.aggregate(
            total=models.Sum('points')
        )['total'] or 0
        
        # Usuarios por nivel
        levels_stats = ManagerData.objects.values('acc_level').annotate(
            count=models.Count('acc_level')
        )
        
        context = {
            'total_users': total_users,
            'staff_users': staff_users,
            'active_users': active_users,
            'total_managers': total_managers,
            'total_points': total_points,
            'levels_stats': levels_stats,
            'user': request.user
        }
        
        return render(request, 'manager/admin_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error al cargar dashboard admin para {request.user.username}: {e}")
        return render(request, 'manager/admin_dashboard.html', {
            'error': 'Error al cargar el dashboard administrativo.'
        })


@login_required
def search_users_ajax(request):
    """Vista que maneja las búsquedas AJAX"""
    # 1. Verificar permisos (solo staff)
    if not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permiso para realizar esta acción.'}, status=403)
    
    # 2. Obtener el término de búsqueda
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    per_page = 10  # Número de resultados por página
    
    if not query:
        return JsonResponse({'users': [], 'total': 0, 'page': page, 'per_page': per_page})
    
    # 3. Filtrar usuarios en la base de datos
    users_qs = CustomUser.objects.filter(
        models.Q(username__icontains=query) |
        models.Q(first_name__icontains=query) |
        models.Q(last_name__icontains=query)
    ).order_by('username')
    
    total_results = users_qs.count()
    
    # 4. Paginar resultados
    start = (page - 1) * per_page
    end = start + per_page
    users_page = users_qs[start:end]
    
    users_data = [{
        'id': user.id,
        'username': user.username,
        'full_name': user.get_full_name(),
        'email': user.email,
        'is_staff': user.is_staff,
        'is_active': user.is_active
    } for user in users_page]
    
    # 5. Devolver JSON con usuarios encontrados
    return JsonResponse({
        'users': users_data,
        'total': total_results,
        'page': page,
        'per_page': per_page
    })

def manager_modification(request, user_id):
    """
    Vista para que un administrador modifique la información del ManagerData de un usuario.
    Si el usuario no tiene un ManagerData asociado, se crea uno nuevo.
    """
    manager_info = ManagerData.objects.filter(user_id=user_id).first()
    
    if not manager_info:
        manager_info = create_manager(request.user)
        if not manager_info:
            return render(request, 'manager/account_manager.html', {
                'error': 'No se pudo crear la información del manager.'
            })

    if request.method == 'POST':
        form = ManagerDataForm(request.POST, instance=manager_info)
        if form.is_valid():
            form.save()
            logger.info(f"ManagerData actualizado para {manager_info.user.username} por {request.user.username}")
            return render(request, 'manager/account_manager.html', {
                'manager_info': manager_info,
                'success': 'Información del manager actualizada correctamente.'
            })
        else:
            logger.warning(f"Error en el formulario de ManagerData para {manager_info.user.username}: {form.errors}")
    else:
        form = ManagerDataForm(instance=manager_info)

    return render(request, 'manager/modify_manager.html', {'form': form, 'manager_info': manager_info})

