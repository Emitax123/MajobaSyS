from django.shortcuts import render
from .forms import CustomUserCreationForm
from manager.views import create_manager
from django.contrib.auth.decorators import login_required
import logging
logger = logging.getLogger(__name__)



def user_create_view(request):
    print("Metodo de request:", request.method)
    if request.method == 'POST':
        try:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                # Ademas deberiamos crear automáticamente un ManagerData asociado
                print("Usuario creado, ahora creando ManagerData...")
                create_manager(form.instance)
                print("ManagerData creado.")
                return render(request, 'users/staff_template.html')
        except Exception as e:
            logger.error(f"Error al crear usuario: {e}")
    form = CustomUserCreationForm()
    return render(request, 'users/user_create.html', {'form': form})


