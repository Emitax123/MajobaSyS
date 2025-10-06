from django.db import models
from django.contrib.auth.models import AbstractUser
import logging

logger = logging.getLogger('users')


class CustomUser(AbstractUser):
    """
    Custom User model without email requirement.
    Perfect for manually created accounts.
    """
    # Remover email como campo requerido
    email = models.EmailField(blank=True, null=True)
    
    # Campos adicionales
    first_name = models.CharField('Nombre', max_length=150, blank=True)
    last_name = models.CharField('Apellido', max_length=150, blank=True)
    phone = models.CharField('Teléfono', max_length=20, blank=True)
    profession = models.CharField('Profesión', max_length=100, blank=True)
    direction = models.CharField('Dirección', max_length=255, blank=True)
    
    # Campos de control
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última actualización', auto_now=True)
    is_active = models.BooleanField('Activo', default=True)

    is_staff = models.BooleanField('Es administrador', default=False)

    # Username es el campo principal para login
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # No requerir email ni otros campos
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'.strip()
        return self.username
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.first_name or self.username
    
    def save(self, *args, **kwargs):
        """Override save para logging."""
        if self.pk:
            logger.info(f"Actualizando usuario: {self.username}")
        else:
            logger.info(f"Creando nuevo usuario: {self.username}")
        super().save(*args, **kwargs)
