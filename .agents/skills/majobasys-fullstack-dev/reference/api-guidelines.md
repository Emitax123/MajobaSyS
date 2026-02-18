# Guías de Diseño de APIs - MajobaSYS

## Principios de Diseño de APIs REST

### 1. RESTful Resource Naming

```
✅ Correcto:
GET    /api/v1/users/              # Lista de usuarios
GET    /api/v1/users/{id}/         # Usuario específico
POST   /api/v1/users/              # Crear usuario
PUT    /api/v1/users/{id}/         # Actualizar completo
PATCH  /api/v1/users/{id}/         # Actualizar parcial
DELETE /api/v1/users/{id}/         # Eliminar usuario

GET    /api/v1/users/{id}/profile/ # Perfil del usuario (nested)
POST   /api/v1/managers/{id}/add-points/  # Acción custom

❌ Incorrecto:
GET    /api/v1/getUsers/           # No usar verbos
POST   /api/v1/user/create/        # No redundante
GET    /api/v1/users/{id}/delete/  # DELETE no GET
```

### 2. Versionado de API

```python
# En urls.py
urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    path('api/v2/', include('api.v2.urls')),  # Futuras versiones
]

# Header alternativo (futuro)
# Accept: application/vnd.majobasys.v1+json
```

### 3. Códigos de Estado HTTP

```python
from rest_framework import status

# Éxito
200 OK              # GET exitoso, datos retornados
201 CREATED         # POST exitoso, recurso creado
204 NO_CONTENT      # DELETE exitoso, sin contenido

# Errores del cliente
400 BAD_REQUEST     # Datos inválidos
401 UNAUTHORIZED    # No autenticado
403 FORBIDDEN       # No autorizado (autenticado pero sin permisos)
404 NOT_FOUND       # Recurso no existe
422 UNPROCESSABLE_ENTITY  # Validación falló

# Errores del servidor
500 INTERNAL_SERVER_ERROR  # Error del servidor
503 SERVICE_UNAVAILABLE    # Servicio no disponible
```

## Estructura de ViewSets DRF

### ViewSet Básico

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class ManagerViewSet(viewsets.ModelViewSet):
    """
    API endpoints para gestión de perfiles de gamificación.
    
    list: Listar todos los perfiles
    retrieve: Obtener un perfil específico
    create: Crear nuevo perfil (admin only)
    update: Actualizar perfil completo
    partial_update: Actualizar perfil parcialmente
    destroy: Eliminar perfil
    """
    queryset = CustomManager.objects.select_related('user')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['acc_level', 'user__is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['points', 'lifetime_points', 'created_at']
    ordering = ['-points']
    
    def get_queryset(self):
        """Optimizar queryset y filtrar según permisos."""
        queryset = super().get_queryset()
        
        # Si no es admin, solo ver su propio perfil
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """
        Agregar puntos a un perfil.
        
        POST /api/v1/managers/{id}/add-points/
        Body: {"points": 100, "reason": "Completó tarea"}
        """
        manager = self.get_object()
        points = request.data.get('points')
        reason = request.data.get('reason', 'No especificada')
        
        if not points or not isinstance(points, int) or points <= 0:
            return Response(
                {'error': 'Los puntos deben ser un número positivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        manager.add_points(points)
        
        return Response({
            'success': True,
            'message': f'Agregados {points} puntos',
            'data': self.get_serializer(manager).data
        }, status=status.HTTP_200_OK)
```

## Serializers

### Serializer Básico

```python
from rest_framework import serializers
from manager.models import CustomManager


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico de usuario para respuestas anidadas."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'email']
        read_only_fields = ['id']


class ManagerSerializer(serializers.ModelSerializer):
    """Serializer completo de CustomManager."""
    
    user = UserBasicSerializer(read_only=True)
    acc_level_display = serializers.CharField(
        source='get_acc_level_display',
        read_only=True
    )
    points_to_next_level = serializers.IntegerField(
        source='get_points_to_next_level',
        read_only=True
    )
    level_progress = serializers.IntegerField(
        source='get_level_progress',
        read_only=True
    )
    
    class Meta:
        model = CustomManager
        fields = [
            'id',
            'user',
            'points',
            'lifetime_points',
            'acc_level',
            'acc_level_display',
            'notifications',
            'points_to_next_level',
            'level_progress',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'lifetime_points']
    
    def validate_points(self, value):
        """Validar que points no sea negativo."""
        if value < 0:
            raise serializers.ValidationError("Los puntos no pueden ser negativos")
        return value
```

## Estructura de Respuestas

### Respuesta Exitosa (Lista)

```json
{
  "count": 100,
  "next": "http://api.example.com/managers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 5,
        "username": "juan_perez",
        "full_name": "Juan Pérez",
        "email": "juan@example.com"
      },
      "points": 2500,
      "lifetime_points": 5000,
      "acc_level": "gold",
      "acc_level_display": "Oro",
      "notifications": 3,
      "points_to_next_level": 0,
      "level_progress": 50,
      "created_at": "2026-01-15T10:30:00Z",
      "updated_at": "2026-02-12T14:20:00Z"
    }
  ]
}
```

### Respuesta Exitosa (Detalle)

```json
{
  "id": 1,
  "user": {
    "id": 5,
    "username": "juan_perez",
    "full_name": "Juan Pérez",
    "email": "juan@example.com"
  },
  "points": 2500,
  "lifetime_points": 5000,
  "acc_level": "gold",
  "acc_level_display": "Oro",
  "notifications": 3,
  "points_to_next_level": 0,
  "level_progress": 50,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-02-12T14:20:00Z"
}
```

### Respuesta de Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Los datos proporcionados son inválidos",
    "details": {
      "points": ["Este campo es requerido"],
      "reason": ["Asegúrate de que este campo no tenga más de 255 caracteres"]
    }
  }
}
```

## Autenticación JWT

### Configuración

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Endpoints de Autenticación

```python
# urls.py
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
```

### Uso desde Cliente (React Native)

```javascript
// Obtener token
const response = await fetch('http://api.example.com/api/v1/auth/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'juan_perez',
    password: 'password123'
  })
});

const { access, refresh } = await response.json();

// Usar token en requests
const managers = await fetch('http://api.example.com/api/v1/managers/', {
  headers: {
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json'
  }
});

// Refresh token cuando expira
const refreshResponse = await fetch('http://api.example.com/api/v1/auth/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh })
});

const { access: newAccess } = await refreshResponse.json();
```

## Paginación

```python
# Usar paginación por defecto (configurada en settings)
# GET /api/v1/managers/?page=2

# Personalizar page size por request
# GET /api/v1/managers/?page=1&page_size=50

# Implementar cursor pagination para mejor performance
from rest_framework.pagination import CursorPagination

class ManagerCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'
```

## Filtros y Búsqueda

```python
# Instalar django-filter
# pip install django-filter

# En ViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ManagerViewSet(viewsets.ModelViewSet):
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['acc_level', 'user__is_active']
    search_fields = ['user__username', 'user__first_name']
    ordering_fields = ['points', 'lifetime_points', 'created_at']

# Uso:
# GET /api/v1/managers/?acc_level=gold
# GET /api/v1/managers/?search=juan
# GET /api/v1/managers/?ordering=-points
```

## Permisos

```python
from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso custom: solo el owner o admin pueden modificar.
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para owner o admin
        return obj.user == request.user or request.user.is_staff

# En ViewSet
class ManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
```

## Throttling (Rate Limiting)

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'burst': '60/minute',
    }
}

# Custom throttle para endpoints específicos
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    rate = '60/min'

class ManagerViewSet(viewsets.ModelViewSet):
    throttle_classes = [BurstRateThrottle]
```

## Documentación con drf-spectacular

```python
# pip install drf-spectacular

# settings/base.py
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'MajobaSYS API',
    'DESCRIPTION': 'API de gamificación para MajobaSYS',
    'VERSION': '1.0.0',
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

## Testing de APIs

```python
from rest_framework.test import APITestCase
from rest_framework import status

class ManagerAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.manager = self.user.manager_user
        self.client.force_authenticate(user=self.user)
    
    def test_list_managers(self):
        """Test listar managers."""
        response = self.client.get('/api/v1/managers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_add_points(self):
        """Test agregar puntos via API."""
        url = f'/api/v1/managers/{self.manager.id}/add-points/'
        data = {'points': 100, 'reason': 'Test'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.manager.refresh_from_db()
        self.assertEqual(self.manager.points, 100)
```

---

**Nota**: Estas guías se actualizarán conforme se implementen las APIs en el proyecto.
