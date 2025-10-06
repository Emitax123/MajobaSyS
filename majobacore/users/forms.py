from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from .models import CustomUser
import logging

logger = logging.getLogger('users')


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario para crear usuarios con campos personalizados.
    Perfecto para registro manual por administradores.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 
                 'profession', 'is_staff', 'direction', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilos a campos heredados
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.profession = self.cleaned_data['profession']
        user.direction = self.cleaned_data['direction']
        user.is_staff = self.cleaned_data['is_staff']
        user.is_active = True  # Activar usuario por defecto
        
        if commit:
            user.save()
            logger.info(f"Usuario creado mediante formulario: {user.username}")
        
        return user

