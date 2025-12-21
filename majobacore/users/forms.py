from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser
import logging

logger = logging.getLogger('users')


class CustomLoginForm(AuthenticationForm):
    """
    Formulario personalizado de login con estilos y validación mejorada
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autocomplete': 'username',
            'autofocus': True
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'
        }),
        label='Contraseña'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error
        self.error_messages['invalid_login'] = 'Usuario o contraseña incorrectos.'
        self.error_messages['inactive'] = 'Esta cuenta está desactivada.'
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Verificar que el usuario existe
            try:
                user = CustomUser.objects.get(username=username)
                if not user.is_active:
                    raise forms.ValidationError('Tu cuenta está desactivada. Contacta al administrador.')
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('Usuario o contraseña incorrectos.')
        
        return super().clean()


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
        
        # Personalizar mensajes de error por defecto
        for field_name, field in self.fields.items():
            if 'required' not in field.error_messages:
                field.error_messages['required'] = 'Este campo es obligatorio.'

        self.fields['username'].error_messages = {
            'invalid': 'Ingresa un nombre de usuario válido.',
            'unique': 'Este nombre de usuario ya está en uso.'
        }
        
        self.fields['email'].error_messages = {
            'invalid': 'Ingresa un email válido.',
            'unique': 'Este email ya está registrado.'
        }
        
        self.fields['password2'].error_messages = {
            'required': 'Debes confirmar la contraseña.',
        }
        
        # Aplicar estilos a campos heredados
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    # Personalizar mensajes de error del UserCreationForm
    error_messages = {
        'password_mismatch': 'Las contraseñas no coinciden. Por favor, verifica que ambas sean iguales.',
    }
    
    def clean_password1(self):
        """Validar la primera contraseña con los validadores de Django"""
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password(password1, self.instance)
            except ValidationError as error:
                # Personalizar mensajes de validación de contraseña
                custom_messages = []
                for message in error.messages:
                    if 'This password is too short' in message:
                        custom_messages.append('La contraseña debe tener al menos 8 caracteres.')
                    elif 'This field is required' in message:
                        custom_messages.append('Este campo es obligatorio.')
                    elif 'This password is too common' in message:
                        custom_messages.append('Esta contraseña es muy común. Usa una más segura.')
                    elif 'This password is entirely numeric' in message:
                        custom_messages.append('La contraseña no puede ser completamente numérica.')
                    elif 'The password is too similar to the' in message:
                        custom_messages.append('La contraseña es muy similar a tu información personal.')
                    else:
                        custom_messages.append(message)
                raise forms.ValidationError(custom_messages)
        return password1
    
    def clean_password2(self):
        """Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden. Por favor, verifica que ambas sean iguales.")
        elif password2 and not password1:
            raise forms.ValidationError("Debes ingresar la primera contraseña.")
        
        return password2
    
    def clean(self):
        """Validación adicional para el formulario completo"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # Verificar que ambas contraseñas estén presentes
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden. Por favor, verifica que ambas sean iguales.")
        
        return cleaned_data
    
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


class CustomUserChangeForm(UserChangeForm):
    """
    Formulario para modificar usuarios existentes.
    Basado en UserChangeForm que maneja correctamente las contraseñas opcionales.
    """
    password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (opcional)'
        }),
        required=False,
        help_text='Deja en blanco si no quieres cambiar la contraseña.'
    )
    
    password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 
                 'profession', 'is_staff', 'direction', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar mensajes de error para todos los campos
        for field_name, field in self.fields.items():
            if field.required:
                field.error_messages['required'] = 'Este campo es obligatorio.'
        
        # Mensajes específicos para campos particulares
        self.fields['username'].error_messages.update({
            'invalid': 'Ingresa un nombre de usuario válido.',
            'unique': 'Este nombre de usuario ya está en uso.'
        })
        
        self.fields['email'].error_messages.update({
            'invalid': 'Ingresa un email válido.',
            'unique': 'Este email ya está registrado.'
        })
        
        # Aplicar estilos a campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Teléfono'
        })
        self.fields['profession'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Profesión'
        })
        self.fields['direction'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Dirección'
        })
        self.fields['is_staff'].widget.attrs.update({
            'class': 'form-check-input'
        })
        self.fields['is_active'].widget.attrs.update({
            'class': 'form-check-input'
        })
        
        # Remover el campo de contraseña por defecto del UserChangeForm
        if 'password' in self.fields:
            del self.fields['password']

    def clean_password2(self):
        """Validar que las contraseñas coincidan si se proporciona una nueva"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return password2

    def clean_username(self):
        """Validar que el username sea único, excluyendo el usuario actual"""
        username = self.cleaned_data.get('username')
        
        if username:
            # Excluir el usuario actual de la validación de unicidad
            queryset = CustomUser.objects.filter(username=username)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        
        return username

    def clean_email(self):
        """Validar que el email sea único, excluyendo el usuario actual"""
        email = self.cleaned_data.get('email')
        
        if email:
            # Excluir el usuario actual de la validación de unicidad
            queryset = CustomUser.objects.filter(email=email)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Este email ya está registrado.')
        
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Solo cambiar la contraseña si se proporciona una nueva
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        
        if commit:
            user.save()
            logger.info(f"Usuario {user.username} modificado exitosamente")
        
        return user

