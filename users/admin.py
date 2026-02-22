from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin personalizado para CustomUser.
    Perfecto para crear usuarios manualmente.
    """
    # Campos que aparecen en la lista de usuarios
    list_display = ('username', 'get_full_name', 'profession', 'direction', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'direction', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'profession', 'direction')
    ordering = ('-created_at',)
    
    # Campos en el formulario de edición
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Información Laboral', {
            'fields': ('profession', 'direction')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos al crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 
                      'profession', 'direction', 'is_active', 'is_staff'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    # Filtros horizontales para grupos y permisos
    filter_horizontal = ('groups', 'user_permissions')
    
    def get_full_name(self, obj):
        """Mostrar nombre completo en la lista."""
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'
