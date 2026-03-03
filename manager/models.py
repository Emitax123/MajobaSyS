from django.db import models
from users.models import CustomUser
# Create your models here.


class Client(models.Model):
    """
    Modelo que representa un cliente asociado a un usuario del sistema.
    Cada usuario puede tener múltiples clientes, y cada cliente puede
    estar vinculado a múltiples proyectos.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Usuario'
    )
    name = models.CharField(max_length=255, verbose_name='Nombre')
    phone = models.CharField(max_length=20, verbose_name='Teléfono')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Usuario'
    )
    client = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT,
        related_name='projects',
        verbose_name='Cliente',
        null=True,
        blank=True
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
        """
        Devuelve el tiempo transcurrido desde la creación de la notificación en español.

        Returns:
            str: Cadena legible como "ahora", "hace 5 minutos", "hace 2 horas", etc.
        """
        from django.utils import timezone

        ahora = timezone.now()
        diferencia = ahora - self.created_at
        segundos = int(diferencia.total_seconds())

        if segundos < 60:
            return "ahora"
        elif segundos < 3600:
            minutos = segundos // 60
            return f"hace {minutos} {'minuto' if minutos == 1 else 'minutos'}"
        elif segundos < 86400:
            horas = segundos // 3600
            return f"hace {horas} {'hora' if horas == 1 else 'horas'}"
        elif segundos < 2592000:
            dias = segundos // 86400
            return f"hace {dias} {'día' if dias == 1 else 'días'}"
        elif segundos < 31536000:
            meses = segundos // 2592000
            return f"hace {meses} {'mes' if meses == 1 else 'meses'}"
        else:
            años = segundos // 31536000
            return f"hace {años} {'año' if años == 1 else 'años'}"
    
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
    
    def _nivel_canonico(self):
        """
        Devuelve el nivel válido basado en los puntos actuales.
        Si acc_level tiene un valor fuera de los choices, lo recalcula
        desde los puntos en lugar de fallar silenciosamente.

        Returns:
            str: Uno de los cinco valores válidos de acc_level.
        """
        NIVELES_VALIDOS = {'principiante', 'intermedio', 'avanzado', 'experto', 'maestro'}
        if self.acc_level in NIVELES_VALIDOS:
            return self.acc_level
        # Valor corrupto/heredado: recalcular desde puntos
        import logging
        logging.getLogger('manager').warning(
            "ManagerData pk=%s tiene acc_level inválido '%s'. "
            "Recalculando desde puntos=%s.",
            self.pk, self.acc_level, self.points,
        )
        if self.points >= 10000:
            return 'maestro'
        elif self.points >= 5000:
            return 'experto'
        elif self.points >= 2000:
            return 'avanzado'
        elif self.points >= 500:
            return 'intermedio'
        return 'principiante'

    @property
    def points_for_next_level(self):
        """
        Calcula los puntos que faltan para alcanzar el siguiente nivel.

        Returns:
            int: Puntos restantes. Retorna 0 si ya es Maestro (nivel máximo).
        """
        next_level_thresholds = {
            'principiante': 500,
            'intermedio': 2000,
            'avanzado': 5000,
            'experto': 10000,
            'maestro': 0,  # Nivel máximo, no hay siguiente nivel
        }
        threshold = next_level_thresholds[self._nivel_canonico()]

        if threshold == 0:
            return 0

        return max(0, threshold - self.points)

    @property
    def progress_percentage(self):
        """
        Calcula el porcentaje de progreso dentro del nivel actual (0–100).

        Returns:
            int: Porcentaje entero entre 0 y 100.
        """
        level_thresholds = {
            'principiante': (0, 500),
            'intermedio': (500, 2000),
            'avanzado': (2000, 5000),
            'experto': (5000, 10000),
            'maestro': (10000, float('inf')),
        }
        min_points, max_points = level_thresholds[self._nivel_canonico()]

        if max_points == float('inf'):
            return 100  # Nivel máximo alcanzado

        progress = ((self.points - min_points) / (max_points - min_points)) * 100
        return int(max(0, min(100, progress)))

    @property
    def next_level_display(self):
        """
        Retorna el nombre legible (capitalizado) del siguiente nivel.

        Returns:
            str: Nombre del siguiente nivel, o 'Maestro' si ya es el máximo.
        """
        next_levels = {
            'principiante': 'Intermedio',
            'intermedio': 'Avanzado',
            'avanzado': 'Experto',
            'experto': 'Maestro',
            'maestro': 'Maestro',
        }
        return next_levels[self._nivel_canonico()]



    def update_level(self):
        """Actualizar el nivel basado en puntos totales"""
        if self.points >= 10000:
            self.acc_level = 'maestro'
        elif self.points >= 5000:
            self.acc_level = 'experto'
        elif self.points >= 2000:
            self.acc_level = 'avanzado'
        elif self.points >= 500:
            self.acc_level = 'intermedio'
        else:
            self.acc_level = 'principiante'
        self.save()