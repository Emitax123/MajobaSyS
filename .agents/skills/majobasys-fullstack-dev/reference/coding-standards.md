# Estándares de Código - MajobaSYS

## Principios Generales

1. **Claridad sobre brevedad** - Código legible es más importante que código corto
2. **Documentación en español** - Docstrings, comentarios y mensajes en español
3. **Consistencia** - Seguir patrones establecidos en el proyecto
4. **Seguridad primero** - Validar datos, usar validadores, evitar hardcodear secrets
5. **Performance consciente** - Optimizar queries, usar índices, evitar N+1 problems

## Estructura de Archivos Python

### Orden de Imports

```python
"""
Docstring del módulo (si aplica).
Describe qué hace este archivo y para qué sirve.
"""

# 1. Imports de stdlib (Python estándar)
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# 2. Imports de Django
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# 3. Imports de third-party packages
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

# 4. Imports locales (del proyecto)
from users.models import CustomUser
from manager.models import CustomManager

# Logger al inicio (después de imports)
logger = logging.getLogger(__name__)  # o logger = logging.getLogger('app_name')

# Constantes (si aplican)
MAX_POINTS = 1000000
DEFAULT_LEVEL = 'bronze'

# Clases y funciones
```

**Herramientas recomendadas** (futuro):
- `isort` para ordenar imports automáticamente
- `black` para formateo consistente

## Nombrado de Variables y Funciones

### Convenciones

```python
# Variables y funciones: snake_case
user_points = 100
total_lifetime_points = 5000

def calculate_level_progress():
    pass

def get_points_to_next_level():
    pass

# Clases: PascalCase
class CustomManager(models.Model):
    pass

class UserSerializer(serializers.ModelSerializer):
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_POINTS_PER_ACTION = 1000
LEVEL_THRESHOLDS = {
    'bronze': 0,
    'silver': 500,
    'gold': 2000,
}

# Variables privadas (convención): _prefijo
def _internal_calculation():
    pass

_cache_timeout = 300
```

### Nombres Descriptivos

```python
# ❌ Evitar nombres poco claros
def proc():
    pass

x = 100
tmp = get_data()

# ✅ Nombres descriptivos
def process_user_points():
    pass

points_awarded = 100
user_manager_profile = get_manager_profile()
```

## Modelos Django

### Estructura de un Modelo

```python
from django.db import models
from django.core.validators import MinValueValidator
import logging

logger = logging.getLogger('app_name')


class ModeloEjemplo(models.Model):
    """
    Descripción del modelo.
    
    Este modelo representa... y se utiliza para...
    """
    
    # 1. Campos de relación primero
    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='ejemplo',
        verbose_name='Usuario'
    )
    
    # 2. Campos de datos
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre del ejemplo'
    )
    
    puntos = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Puntos',
        help_text='Puntos acumulados'
    )
    
    # 3. Campos booleanos
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # 4. Campos de timestamp al final
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ejemplo'
        verbose_name_plural = 'Ejemplos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['activo', '-puntos']),
        ]
    
    def __str__(self):
        """Representación string del modelo."""
        return f"{self.nombre} - {self.puntos} puntos"
    
    # Métodos custom después de __str__
    def metodo_ejemplo(self, parametro):
        """
        Descripción del método.
        
        Args:
            parametro (tipo): Descripción
        
        Returns:
            tipo: Descripción del retorno
        """
        logger.info(f"Ejecutando método para {self.nombre}")
        # lógica aquí
        return resultado
```

### Validadores Obligatorios

**Siempre usar validadores en campos numéricos**:

```python
from django.core.validators import MinValueValidator, MaxValueValidator

# Campos numéricos que no pueden ser negativos
puntos = models.IntegerField(
    default=0,
    validators=[MinValueValidator(0)],  # ✅ Obligatorio
    verbose_name='Puntos'
)

# Campos con rango específico
edad = models.IntegerField(
    validators=[MinValueValidator(18), MaxValueValidator(100)],
    verbose_name='Edad'
)

# Campos de porcentaje
progreso = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    validators=[MinValueValidator(0), MaxValueValidator(100)],
    verbose_name='Progreso (%)'
)
```

### Índices de Base de Datos

**Agregar índices para campos frecuentemente consultados**:

```python
class Meta:
    indexes = [
        # Ordenamiento común
        models.Index(fields=['-created_at']),
        
        # Filtros frecuentes
        models.Index(fields=['activo']),
        models.Index(fields=['acc_level']),
        
        # Combinaciones usadas en queries
        models.Index(fields=['-points', '-created_at']),
        
        # Búsquedas de texto (con compatibilidad PostgreSQL)
        models.Index(fields=['nombre']),
    ]
```

## Docstrings (Español)

### Para Funciones y Métodos

```python
def agregar_puntos(self, cantidad, razon=None):
    """
    Agregar puntos al usuario y actualizar su nivel automáticamente.
    
    Este método incrementa los puntos actuales y los puntos de por vida,
    luego recalcula el nivel del usuario basándose en los umbrales definidos.
    
    Args:
        cantidad (int): Cantidad de puntos a agregar (debe ser positivo)
        razon (str, optional): Descripción de por qué se agregan los puntos.
            Defaults to None.
    
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    
    Raises:
        ValueError: Si cantidad es negativa o cero
        TypeError: Si cantidad no es un entero
    
    Example:
        >>> manager.agregar_puntos(100, razon="Completó tarea")
        True
        >>> manager.points
        100
        >>> manager.lifetime_points
        100
    """
    if not isinstance(cantidad, int):
        raise TypeError("La cantidad debe ser un entero")
    
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva")
    
    self.points += cantidad
    self.lifetime_points += cantidad
    self.update_level()
    
    logger.info(
        f"Usuario {self.user.username} ganó {cantidad} puntos. "
        f"Razón: {razon or 'No especificada'}"
    )
    
    self.save()
    return True
```

### Para Clases

```python
class CustomManager(models.Model):
    """
    Perfil de gamificación vinculado a cada usuario.
    
    Este modelo gestiona el sistema de puntos y niveles. Cada usuario
    tiene exactamente un CustomManager creado automáticamente mediante
    signals al momento de crear el usuario.
    
    Attributes:
        user: Relación OneToOne con CustomUser
        points: Puntos actuales disponibles para gastar
        lifetime_points: Puntos totales acumulados (determina nivel)
        acc_level: Nivel actual (bronze, silver, gold, platinum, diamond)
        notifications: Contador de notificaciones no leídas
    
    Sistema de Niveles:
        - Bronze: 0-499 puntos lifetime
        - Silver: 500-1,999 puntos lifetime
        - Gold: 2,000-4,999 puntos lifetime
        - Platinum: 5,000-9,999 puntos lifetime
        - Diamond: 10,000+ puntos lifetime
    
    Note:
        El nivel se basa en lifetime_points, no en points actuales.
        Gastar puntos no reduce el nivel del usuario.
    """
    # ... campos
```

### Para Módulos

```python
"""
Sistema de gamificación para MajobaSYS.

Este módulo contiene los modelos relacionados con el sistema de puntos,
niveles y recompensas. Incluye lógica para:

- Gestión de puntos (agregar, gastar, transferir)
- Actualización automática de niveles
- Cálculo de progreso hacia el siguiente nivel
- Historial de transacciones

Author: Equipo MajobaSYS
Version: 1.1.0
"""
```

## Logging

### Configurar Logger

```python
import logging

# Al inicio del archivo, después de imports
logger = logging.getLogger(__name__)  # Opción 1: usa el nombre del módulo

# O con nombre explícito de app
logger = logging.getLogger('manager')  # Opción 2: para app específica
```

### Niveles de Logging

```python
# DEBUG: Información detallada para debugging
logger.debug(f"Calculando nivel para user_id={self.user.id}")

# INFO: Eventos importantes normales
logger.info(f"Usuario {self.user.username} subió a nivel {self.acc_level}")

# WARNING: Advertencias, pero la app continúa funcionando
logger.warning(f"Usuario intentó gastar {points} puntos pero solo tiene {self.points}")

# ERROR: Errores que afectan funcionalidad
logger.error(f"Error al procesar puntos: {str(e)}")

# CRITICAL: Errores críticos que pueden detener la app
logger.critical(f"Base de datos inaccesible: {str(e)}")
```

### Patrones de Logging

```python
# ✅ Logging informativo con contexto
logger.info(
    f"Usuario {self.user.username} ganó {points} puntos. "
    f"Total actual: {self.points}, Nivel: {self.acc_level}"
)

# ✅ Logging de cambios importantes
if old_level != self.acc_level:
    logger.info(
        f"¡Usuario {self.user.username} subió de nivel! "
        f"{old_level} → {self.acc_level}"
    )

# ✅ Logging de errores con traceback
try:
    resultado = operacion_critica()
except Exception as e:
    logger.error(
        f"Error en operacion_critica para user {self.user.id}: {str(e)}",
        exc_info=True  # Incluye traceback
    )
    raise

# ❌ Evitar logging excesivo
# No hacer esto en un loop:
for item in items:
    logger.info(f"Procesando {item}")  # Saturará logs
```

## Vistas y ViewSets

### Vistas Basadas en Clases (CBV)

```python
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin


class PerfilListView(LoginRequiredMixin, ListView):
    """
    Lista todos los perfiles de usuario con paginación.
    
    Requiere autenticación. Muestra perfiles ordenados por puntos
    descendente con 20 items por página.
    """
    model = CustomManager
    template_name = 'manager/perfil_list.html'
    context_object_name = 'perfiles'
    paginate_by = 20
    
    def get_queryset(self):
        """Optimizar query con select_related."""
        return CustomManager.objects.select_related('user').order_by('-points')
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional."""
        context = super().get_context_data(**kwargs)
        context['total_usuarios'] = CustomManager.objects.count()
        return context
```

### ViewSets de DRF (Futuro)

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ManagerViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar perfiles de gamificación.
    
    Endpoints:
        - GET /api/managers/ - Listar perfiles
        - POST /api/managers/ - Crear perfil (admin only)
        - GET /api/managers/{id}/ - Detalle de perfil
        - PUT /api/managers/{id}/ - Actualizar perfil
        - DELETE /api/managers/{id}/ - Eliminar perfil
        - POST /api/managers/{id}/add-points/ - Agregar puntos
    """
    queryset = CustomManager.objects.select_related('user')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """
        Agregar puntos a un perfil específico.
        
        Body:
            {
                "points": 100,
                "reason": "Completó tarea X"
            }
        """
        manager = self.get_object()
        points = request.data.get('points')
        reason = request.data.get('reason')
        
        if not points or points <= 0:
            return Response(
                {'error': 'Los puntos deben ser un número positivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        manager.add_points(points)
        logger.info(
            f"API: Agregados {points} puntos a {manager.user.username}. "
            f"Razón: {reason}"
        )
        
        serializer = self.get_serializer(manager)
        return Response(serializer.data)
```

## Tests

### Estructura de Tests

```python
from django.test import TestCase
from users.models import CustomUser
from manager.models import CustomManager


class CustomManagerTestCase(TestCase):
    """Tests para el modelo CustomManager."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.manager = self.user.manager_user
    
    def test_add_points_increases_both_points_and_lifetime(self):
        """Agregar puntos debe incrementar points y lifetime_points."""
        initial_points = self.manager.points
        initial_lifetime = self.manager.lifetime_points
        
        self.manager.add_points(100)
        
        self.assertEqual(self.manager.points, initial_points + 100)
        self.assertEqual(self.manager.lifetime_points, initial_lifetime + 100)
    
    def test_level_updates_correctly(self):
        """El nivel debe actualizarse al cruzar umbrales."""
        self.assertEqual(self.manager.acc_level, 'bronze')
        
        self.manager.add_points(500)
        self.assertEqual(self.manager.acc_level, 'silver')
        
        self.manager.add_points(1500)
        self.assertEqual(self.manager.acc_level, 'gold')
    
    def test_spend_points_does_not_affect_level(self):
        """Gastar puntos no debe cambiar el nivel."""
        self.manager.add_points(2500)  # Gold level
        self.assertEqual(self.manager.acc_level, 'gold')
        
        self.manager.spend_points(2000)  # Gastar casi todos
        self.assertEqual(self.manager.acc_level, 'gold')  # Nivel no cambia
        self.assertEqual(self.manager.points, 500)
        self.assertEqual(self.manager.lifetime_points, 2500)
```

## Comentarios

### Cuándo Comentar

```python
# ✅ Comentar lógica compleja o no obvia
def calculate_complex_bonus(user, actions):
    # Aplicar multiplicador exponencial basado en racha de días consecutivos
    # Fórmula: bonus = base * (1.1 ^ consecutive_days)
    consecutive_days = user.get_consecutive_active_days()
    multiplier = 1.1 ** min(consecutive_days, 30)  # Cap a 30 días
    
    return base_points * multiplier

# ✅ Comentar decisiones de diseño
class CustomManager(models.Model):
    # Separamos points y lifetime_points para permitir gasto de puntos
    # sin afectar el nivel del usuario (nivel basado en lifetime_points)
    points = models.IntegerField(default=0)
    lifetime_points = models.IntegerField(default=0)

# ✅ Comentar workarounds temporales
def process_data(data):
    # TODO: Optimizar este loop cuando tengamos más de 10k registros
    # Actualmente aceptable para < 1k registros
    for item in data:
        process_item(item)

# ❌ No comentar lo obvio
user = CustomUser.objects.get(pk=1)  # Get user with id 1  ← Innecesario
```

## Manejo de Errores

### Try-Except Patterns

```python
# ✅ Capturar excepciones específicas
try:
    manager = CustomManager.objects.get(user=user)
except CustomManager.DoesNotExist:
    logger.warning(f"Manager profile not found for user {user.username}")
    manager = CustomManager.objects.create(user=user)
except Exception as e:
    logger.error(f"Unexpected error fetching manager: {str(e)}", exc_info=True)
    raise

# ✅ Validar inputs
def add_points(self, points):
    if not isinstance(points, int):
        raise TypeError("Los puntos deben ser un entero")
    
    if points <= 0:
        raise ValueError("Los puntos deben ser positivos")
    
    # ... lógica

# ✅ Reraise después de logging
try:
    critical_operation()
except DatabaseError as e:
    logger.critical(f"Database error: {str(e)}", exc_info=True)
    raise  # Propagar la excepción
```

## Seguridad

### Evitar Hardcodear Secrets

```python
# ❌ Nunca hacer esto
SECRET_KEY = 'django-insecure-123456'
API_KEY = 'sk-abcdef123456'

# ✅ Usar variables de entorno
from decouple import config

SECRET_KEY = config('SECRET_KEY')
API_KEY = config('API_KEY')
```

### Validar Inputs de Usuario

```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def process_user_input(email, age):
    # Validar email
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError("Email inválido")
    
    # Validar rango
    if not (18 <= age <= 100):
        raise ValueError("Edad debe estar entre 18 y 100")
```

### Queries Seguras

```python
# ✅ Usar ORM (protegido contra SQL injection)
users = CustomUser.objects.filter(username=user_input)

# ❌ NUNCA hacer queries raw sin parametrizar
query = f"SELECT * FROM users WHERE username = '{user_input}'"  # SQL INJECTION!

# ✅ Si necesitas raw SQL, usar parametrización
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE username = %s", [user_input])
```

## Formato de Código

### Longitud de Línea

- **Máximo 100 caracteres** por línea (más legible que 79)
- Dividir líneas largas lógicamente

```python
# ✅ Dividir argumentos de función
resultado = funcion_con_muchos_parametros(
    parametro1=valor1,
    parametro2=valor2,
    parametro3=valor3,
    parametro4=valor4
)

# ✅ Dividir listas/dicts
niveles = {
    'bronze': {'min': 0, 'max': 499, 'color': '#CD7F32'},
    'silver': {'min': 500, 'max': 1999, 'color': '#C0C0C0'},
    'gold': {'min': 2000, 'max': 4999, 'color': '#FFD700'},
}

# ✅ Dividir strings largos
mensaje = (
    "Este es un mensaje muy largo que no cabe en una línea "
    "así que lo dividimos en múltiples líneas para mejorar "
    "la legibilidad del código"
)
```

### Espaciado

```python
# ✅ Espacios alrededor de operadores
total = base + bonus - descuento
resultado = valor * 2

# ✅ No espacio antes de : en dicts/slices
diccionario = {'key': 'value'}
lista[1:5]

# ✅ Dos líneas en blanco entre clases/funciones de nivel superior
class ClaseA:
    pass


class ClaseB:
    pass


def funcion_global():
    pass

# ✅ Una línea en blanco entre métodos de clase
class MiClase:
    def metodo_uno(self):
        pass
    
    def metodo_dos(self):
        pass
```

## Checklist Pre-Commit

Antes de hacer commit, verificar:

- [ ] ✅ Imports ordenados (stdlib → django → third-party → local)
- [ ] ✅ Logger configurado si el módulo lo necesita
- [ ] ✅ Docstrings en español para funciones/clases públicas
- [ ] ✅ Validadores en campos numéricos de modelos
- [ ] ✅ Índices en Meta para campos frecuentemente consultados
- [ ] ✅ Logging apropiado (info, warning, error)
- [ ] ✅ No hay secrets hardcodeados
- [ ] ✅ Queries optimizadas (select_related/prefetch_related)
- [ ] ✅ Tests actualizados si aplica
- [ ] ✅ Comentarios para lógica compleja
- [ ] ✅ Nombres descriptivos de variables/funciones
- [ ] ✅ Manejo de errores apropiado

---

**Nota**: Este documento está vivo y se actualiza conforme el proyecto evoluciona.
