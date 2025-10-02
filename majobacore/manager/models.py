from django.db import models
from users.models import CustomUser

# Create your models here.
class CustomManager(models.Model):
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
            ('bronze', 'Bronce'),
            ('silver', 'Plata'),
            ('gold', 'Oro'),
            ('platinum', 'Platino'),
            ('diamond', 'Diamante'),
        ],
        default='bronze',
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
    
    def update_level(self):
        """Actualizar el nivel basado en puntos totales"""
        if self.lifetime_points >= 10000:
            self.acc_level = 'diamond'
        elif self.lifetime_points >= 5000:
            self.acc_level = 'platinum'
        elif self.lifetime_points >= 2000:
            self.acc_level = 'gold'
        elif self.lifetime_points >= 500:
            self.acc_level = 'silver'
        else:
            self.acc_level = 'bronze'
        self.save()