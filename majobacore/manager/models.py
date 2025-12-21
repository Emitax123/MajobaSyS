from django.db import models
from users.models import CustomUser
from django.utils.timesince import timesince
# Create your models here.

class Project(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Usuario'
    )
    name = models.CharField(max_length=255, verbose_name='Nombre del Proyecto')
    description = models.TextField(blank=True, verbose_name='Descripción')
    location = models.CharField(max_length=255, blank=True, verbose_name='Ubicación')
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Fin')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuario'
    )
    message = models.CharField(max_length=255, verbose_name='Mensaje')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_read = models.BooleanField(default=False, verbose_name='Leído')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
    
    def time_elapsed(self):
        
        return timesince(self.created_at)
    
    def __str__(self):
        return f"Notificación para {self.user.username}: {self.message[:20]}"
    

class ManagerData(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='manager_user',
        verbose_name='Usuario'
    )
    
    points = models.IntegerField(
        default=0,
        verbose_name='Puntos'
    )
    acc_level = models.CharField(
              max_length=20,
        choices=[
            ('principiante', 'Principiante'),
            ('intermedio', 'Intermedio'),
            ('avanzado', 'Avanzado'),
            ('experto', 'Experto'),
            ('maestro', 'Maestro'),
        ],
        default='principiante',
        verbose_name='Nivel de Cuenta'
    )
    notifications = models.IntegerField(
        default=0,
        verbose_name='Notificaciones'
    )

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-points', '-created_at']

    def __str__(self):
        return f"Perfil de {self.user.username} - {self.points} puntos"

    def add_points(self, points):
        """Agregar puntos al usuario"""
        self.points += points
        self.save()
    
    def spend_points(self, points):
        """Gastar puntos del usuario"""
        if self.points >= points:
            self.points -= points
            self.save()
            return True
        return False
    
    def points_for_next_level(self):
        """Calcular los puntos necesarios para el siguiente nivel"""
        next_level_thresholds = {
            'principiante': 500,
            'intermedio': 2000,
            'avanzado': 5000,
            'experto': 10000,
            'maestro': 0  # Nivel máximo, no hay siguiente nivel
        }
        threshold = next_level_thresholds.get(self.acc_level, 0)
        
        if threshold == 0:  # Ya está en el nivel máximo
            return 0
        
        return max(0, threshold - self.points)
    
    def progress_percentage(self):
        """Calcular el porcentaje de progreso hacia el siguiente nivel"""
        level_thresholds = {
            'principiante': (0, 500),
            'intermedio': (500, 2000),
            'avanzado': (2000, 5000),
            'experto': (5000, 10000),
            'maestro': (10000, float('inf'))
        }
        
        min_points, max_points = level_thresholds.get(self.acc_level, (0, 500))
        
        if max_points == float('inf'):
            return 100  # Nivel máximo alcanzado
        
        # Calcular el progreso dentro del nivel actual
        progress = ((self.points - min_points) / (max_points - min_points)) * 100
        return max(0, min(100, progress))  # Asegurar que esté entre 0 y 100
    
    def get_next_level_display(self):
        """Obtener el nombre del siguiente nivel"""
        next_levels = {
            'principiante': 'intermedio',
            'intermedio': 'avanzado',
            'avanzado': 'experto',
            'experto': 'maestro',
            'maestro': 'maestro'  # Nivel máximo
        }
        return next_levels.get(self.acc_level, 'principiante')



    def update_level(self):
        """Actualizar el nivel basado en puntos totales"""
        if self.lifetime_points >= 10000:
            self.acc_level = 'maestro'
        elif self.lifetime_points >= 5000:
            self.acc_level = 'experto'
        elif self.lifetime_points >= 2000:
            self.acc_level = 'avanzado'
        elif self.lifetime_points >= 500:
            self.acc_level = 'intermedio'
        else:
            self.acc_level = 'principiante'
        self.save()