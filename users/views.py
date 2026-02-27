from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from manager.views import create_manager
from django.contrib.auth.decorators import login_required
import logging
logger = logging.getLogger(__name__)



def user_create_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                # Crear automáticamente un ManagerData asociado
               
                create_manager(user)
           
                messages.success(request, f'Usuario {user.username} creado exitosamente.')
                request.session['user_created'] = True
                
            
                return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f"Error al crear usuario: {e}")
            
            
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/user_create.html', {'form': form})


def custom_login_view(request):
    """
    Vista personalizada de login con redirección basada en el tipo de usuario
    """
    if request.user.is_authenticated:
        # Si ya está autenticado, redirigir según su tipo
        return redirect_after_login(request)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            remember_me = request.POST.get('remember_me')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    logger.info(f"Usuario {username} ha iniciado sesión exitosamente")
                    
                    # Crear ManagerData si no existe
                    if not hasattr(user, 'manager_user'):
                        create_manager(user)
                    
                    # Manejar "Recordarme"
                    if remember_me:
                        # Sesión persistente: no expira al cerrar el navegador
                        # SESSION_COOKIE_AGE define el máximo; aquí usamos ~1 año
                        request.session.set_expiry(60 * 60 * 24 * 365)
                    else:
                        # Sesión de navegador: expira al cerrar el navegador
                        request.session.set_expiry(0)
                    
                    # Redireccionar según el tipo de usuario
                    return redirect_after_login(request)
                else:
                    messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
                    logger.warning(f"Intento de login con cuenta desactivada: {username}")
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
                logger.warning(f"Intento de login fallido para usuario: {username}")
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'users/login.html')


def redirect_after_login(request):
    """
    Función helper para determinar dónde redirigir después del login
    """
    if request.user.is_staff:
        # Usuarios staff van al dashboard administrativo personalizado
        messages.success(request, f'¡Bienvenido administrador {request.user.get_full_name() or request.user.username}!')
        return redirect('admin_dashboard')
    else:
        # Usuarios normales van al dashboard del manager
        messages.success(request, f'¡Bienvenido {request.user.get_full_name() or request.user.username}!')
        return redirect('manager')


def custom_logout_view(request):
    """
    Vista personalizada de logout
    """
    username = request.user.username if request.user.is_authenticated else 'Usuario'
    logout(request)
    messages.success(request, f'¡Hasta luego {username}! Has cerrado sesión exitosamente.')
    logger.info(f"Usuario {username} ha cerrado sesión")
    return redirect('login')


@login_required
def profile_view(request):
    """
    Vista del perfil del usuario autenticado
    """
    try:
        # Asegurarse de que el usuario tenga ManagerData
        if not hasattr(request.user, 'manager_user'):
            create_manager(request.user)
        
        manager_data = request.user.manager_user
        return render(request, 'users/profile.html', {
            'user': request.user,
            'manager_data': manager_data
        })
    except Exception as e:
        logger.error(f"Error al cargar perfil del usuario {request.user.username}: {e}")
        messages.error(request, 'Error al cargar tu perfil.')
        return redirect('index')

def user_modification(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Obtener información del manager si existe
        manager_info = None
        try:
            manager_info = user.manager_user
        except:
            pass
        
        if request.method == 'POST':
            # Usar el formulario correcto para modificación
            form = CustomUserChangeForm(request.POST, instance=user)
            if form.is_valid():
                updated_user = form.save()
                messages.success(request, f'Usuario {updated_user.username} modificado exitosamente.')
                return redirect('manager_modification', user_id=updated_user.id)
            else:
                # Si el formulario no es válido, se renderiza con los errores
                messages.error(request, 'Por favor, corrige los errores en el formulario.')
        else:
            # Usar el formulario correcto para modificación
            form = CustomUserChangeForm(instance=user)
        
        return render(request, 'users/user_modify.html', {
            'form': form, 
            'user': user,
            'manager_info': manager_info,
            'user_id': user_id
        })
        
    except CustomUser.DoesNotExist:
        logger.error(f"Usuario con id {user_id} no encontrado.")
        messages.error(request, 'Usuario no encontrado.')
        return redirect('admin_dashboard')
