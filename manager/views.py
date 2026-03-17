from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Client, ManagerData, Project, Notification
from .forms import ClientForm, ManagerDataForm, ProjectForm
from .services import create_manager, create_notification
from users.models import CustomUser
from django.db import models
from django.db.models import F
from django.db import transaction
from django.shortcuts import redirect
import logging
logger = logging.getLogger(__name__)

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
                'acc_level': 'principiante',
                'notifications': 0
            }
        )
        #Obtener proyectos asociados al usuario
        
        projects = Project.objects.filter(user=request.user).all()[:3]
        print(projects)
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        if created:
            logger.info(f"ManagerData creado para el usuario {request.user.username}")
        
        return render(request, 'manager/account_manager.html', {
            'manager_info': manager_info,
            'user': request.user,
            'projects': projects,
            'notifications': notifications,
        })
    except Exception as e:
        logger.error(f"Error al cargar ManagerData para {request.user.username}: {e}")
        return render(request, 'manager/account_manager.html', {
            'error': 'Error al cargar la información del manager.'
        })

def create_project_view(request):
    """
    Vista para crear un nuevo proyecto asociado al usuario autenticado.

    Si el POST incluye ``new_client_name`` (no vacío), se crea un nuevo
    cliente en el momento y se asigna al proyecto, ignorando el campo
    ``client`` del formulario. En caso contrario, el cliente proviene del
    campo ``client`` del formulario.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user

            new_client_name = form.cleaned_data.get('new_client_name', '').strip()
            new_client_phone = form.cleaned_data.get('new_client_phone', '').strip()

            if new_client_name:
                new_client = Client.objects.create(
                    name=new_client_name,
                    phone=new_client_phone,
                    user=request.user,
                )
                project.client = new_client
                logger.info(
                    f"Cliente '{new_client.name}' creado al vuelo por {request.user.username}"
                )
            else:
                project.client = form.cleaned_data.get('client')

            project.save()
            logger.info(f"Nuevo proyecto '{project.name}' creado por {request.user.username}")
            return redirect('manager')
        else:
            logger.warning(
                f"Error en el formulario de creación de proyecto por "
                f"{request.user.username}: {form.errors}"
            )
            return render(request, 'manager/create_project.html', {'form': form})
    else:
        form = ProjectForm(user=request.user)
        return render(request, 'manager/create_project.html', {'form': form})

def list_projects_view(request):
    """
    Vista para listar todos los proyectos del usuario autenticado.

    Acepta el parámetro GET ``client`` (ID de cliente) para filtrar
    los proyectos por cliente. Envía al contexto:
    - ``projects``: QuerySet de proyectos (filtrado o completo).
    - ``clients``: todos los clientes del usuario (para el selector de filtro).
    - ``selected_client``: ID del cliente actualmente seleccionado (str o None).
    """
    clients = Client.objects.filter(user=request.user)
    selected_client = request.GET.get('client', '').strip() or None

    projects = (
        Project.objects
        .filter(user=request.user)
        .select_related('client')
        .only('id', 'name', 'location', 'start_date', 'end_date', 'is_active', 'client_id')
        .order_by('-created_at')
    )

    if selected_client:
        projects = projects.filter(client_id=selected_client)
        logger.info(
            f"Proyectos filtrados por cliente ID={selected_client} "
            f"para {request.user.username}"
        )

    return render(request, 'manager/projects_list.html', {
        'projects': projects,
        'clients': clients,
        'selected_client': selected_client,
    })

def modify_project_view(request, project_id):
    """
    Vista para modificar un proyecto existente.

    Filtra el selector de clientes al usuario autenticado pasando
    ``user=request.user`` al instanciar el formulario.
    """
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        logger.warning(
            f"Proyecto con ID {project_id} no encontrado para {request.user.username}"
        )
        return redirect('list_projects')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, user=request.user)
        if form.is_valid():
            form.save()
            logger.info(f"Proyecto '{project.name}' modificado por {request.user.username}")
            return redirect('list_projects')
        else:
            logger.warning(
                f"Error en el formulario de modificación de proyecto por "
                f"{request.user.username}: {form.errors}"
            )
            return render(
                request,
                'manager/modify_project.html',
                {'form': form, 'project': project},
            )
    else:
        form = ProjectForm(instance=project, user=request.user)
        return render(
            request,
            'manager/modify_project.html',
            {'form': form, 'project': project},
        )

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
            'user': request.user,
            'user_created': request.session.pop('user_created', False)
        


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
    print(query)
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
        
        'is_staff': user.is_staff,
        'is_active': user.is_active
    } for user in users_page]
    
    print(users_data)
    print(total_results)
    print(page)
    print(per_page)
    # 5. Devolver JSON con usuarios encontrados
    return JsonResponse({
        'users': users_data,
        'total': total_results,
        'page': page,
        'per_page': per_page
    })


@transaction.atomic
def manager_modification(request, user_id):
    """
    Vista para que un administrador modifique la información del ManagerData de un usuario.
    Si el usuario no tiene un ManagerData asociado, se crea uno nuevo.
    """
    manager_info = ManagerData.objects.filter(user_id=user_id).select_related('user').first()
    
    if not manager_info:
        manager_info = create_manager(request.user)
        if not manager_info:
            return render(request, 'manager/account_manager.html', {
                'error': 'No se pudo crear la información del manager.'
            })

    if request.method == 'POST':
        if request.POST.get('checkbox-option'):
            print('check')
        if request.POST.get('user-points'):
            points = int(request.POST.get('user-points', 0))
            if points > 0:
                ManagerData.objects.filter(id=manager_info.id).update(
                    points=F('points') + points
                )
                manager_info.refresh_from_db()
                manager_info.update_level()  # Sincronizar nivel con los nuevos puntos
            if request.POST.get('checkbox-option'):
                if request.POST.get('description'):
                    create_notification(manager_info, 1, points, request.POST.get('description'))
                else:
                    create_notification(manager_info, 1, points)
        elif request.POST.get('user-minus-points'):
            points = int(request.POST.get('user-minus-points', 0))
            if points > 0:
                # Actualización atómica que previene puntos negativos
                ManagerData.objects.filter(id=manager_info.id).update(
                    points=models.Case(
                        models.When(points__gte=points,
                                    then=F('points') - points),
                        default=0
                    )
                )
                manager_info.refresh_from_db()
                manager_info.update_level()  # Sincronizar nivel con los nuevos puntos
            if request.POST.get('checkbox-option'):
                if request.POST.get('description'):
                    create_notification(manager_info, 2, points, request.POST.get('description'))
                else:
                    create_notification(manager_info, 2, points)

    user = manager_info.user

    return render(request, 'manager/modify_manager.html', { 'manager_info': manager_info, 'user': user})

