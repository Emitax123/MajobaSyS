# Configuración JWT Authentication - MajobaSYS

## Instalación

```bash
pip install djangorestframework-simplejwt
```

## Configuración en Settings

### settings/base.py

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # Para blacklist de tokens
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Para browsable API
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    # Tokens
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    # Algoritmo
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    
    # Headers
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # Claims
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    # Token types
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    # Sliding tokens (opcional, usar si prefieres un solo token)
    # 'SLIDING_TOKEN_LIFETIME': timedelta(hours=5),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
```

## URLs

```python
# majobacore/urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # ...
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
```

## Serializers Custom (Opcional)

```python
# api/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import CustomUser

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer para incluir datos adicionales."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar claims personalizados
        token['username'] = user.username
        token['full_name'] = user.get_full_name()
        token['is_staff'] = user.is_staff
        
        # Datos del manager
        try:
            manager = user.manager_user
            token['acc_level'] = manager.acc_level
            token['points'] = manager.points
        except CustomManager.DoesNotExist:
            token['acc_level'] = 'bronze'
            token['points'] = 0
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar datos del usuario en la respuesta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'full_name': self.user.get_full_name(),
            'email': self.user.email,
        }
        
        return data

# Usar serializer custom en views
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

## Uso en ViewSets

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class ManagerViewSet(viewsets.ModelViewSet):
    """ViewSet protegido con JWT."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomManager.objects.all()
    serializer_class = ManagerSerializer
    
    def get_queryset(self):
        """Filtrar por usuario autenticado."""
        # request.user está disponible gracias a JWT
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)
```

## Permisos Custom

```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso custom: solo el owner puede modificar.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user or request.user.is_staff

# Usar en ViewSet
class ManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
```

## Consumo desde Cliente

### React Native / JavaScript

```javascript
// 1. Login y obtener tokens
const login = async (username, password) => {
  const response = await fetch('http://api.example.com/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  // Guardar tokens en storage
  await AsyncStorage.setItem('access_token', data.access);
  await AsyncStorage.setItem('refresh_token', data.refresh);
  
  return data;
};

// 2. Hacer requests autenticados
const getManagers = async () => {
  const token = await AsyncStorage.getItem('access_token');
  
  const response = await fetch('http://api.example.com/api/v1/managers/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 401) {
    // Token expirado, refresh
    await refreshToken();
    return getManagers(); // Reintentar
  }
  
  return await response.json();
};

// 3. Refresh token
const refreshToken = async () => {
  const refresh = await AsyncStorage.getItem('refresh_token');
  
  const response = await fetch('http://api.example.com/api/v1/auth/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });
  
  if (response.ok) {
    const data = await response.json();
    await AsyncStorage.setItem('access_token', data.access);
    if (data.refresh) {
      // Si ROTATE_REFRESH_TOKENS está activo
      await AsyncStorage.setItem('refresh_token', data.refresh);
    }
    return data.access;
  } else {
    // Refresh token inválido, relogin
    await logout();
    throw new Error('Session expired');
  }
};

// 4. Logout
const logout = async () => {
  await AsyncStorage.removeItem('access_token');
  await AsyncStorage.removeItem('refresh_token');
};

// 5. Verificar token
const verifyToken = async () => {
  const token = await AsyncStorage.getItem('access_token');
  
  const response = await fetch('http://api.example.com/api/v1/auth/verify/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token })
  });
  
  return response.ok;
};
```

### Python / Django (Para testing)

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login/', json={
    'username': 'testuser',
    'password': 'testpass123'
})

tokens = response.json()
access_token = tokens['access']
refresh_token = tokens['refresh']

# Request autenticado
headers = {'Authorization': f'Bearer {access_token}'}
managers = requests.get('http://localhost:8000/api/v1/managers/', headers=headers)
print(managers.json())

# Refresh token
refresh_response = requests.post('http://localhost:8000/api/v1/auth/refresh/', json={
    'refresh': refresh_token
})
new_access = refresh_response.json()['access']
```

## Testing

```python
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

class JWTAuthTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_obtain_token(self):
        """Test obtener token con credenciales válidas."""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_access_protected_endpoint(self):
        """Test acceder a endpoint protegido con token."""
        # Generar token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Hacer request con token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/v1/managers/')
        
        self.assertEqual(response.status_code, 200)
    
    def test_refresh_token(self):
        """Test refresh de access token."""
        # Obtener refresh token
        refresh = RefreshToken.for_user(self.user)
        
        # Refresh
        response = self.client.post('/api/v1/auth/refresh/', {
            'refresh': str(refresh)
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
```

## Migraciones

```bash
# Aplicar migraciones para blacklist
python manage.py migrate rest_framework_simplejwt
```

## Seguridad Best Practices

1. **HTTPS Only**: Siempre usar HTTPS en producción
2. **Short-lived access tokens**: 1 hora o menos
3. **Rotate refresh tokens**: Activar ROTATE_REFRESH_TOKENS
4. **Blacklist tokens**: Usar token_blacklist para logout
5. **Secure storage**: En cliente, usar secure storage (Keychain/Keystore)
6. **No exponer tokens**: No loggear ni exponer tokens en responses
7. **Rate limiting**: Implementar throttling en endpoints de auth

## Troubleshooting

### Error: "Given token not valid for any token type"

**Causa**: Token expirado o inválido  
**Solución**: Refresh token o relogin

### Error: "Token is blacklisted"

**Causa**: Token fue invalidado (logout)  
**Solución**: Usuario debe hacer login nuevamente

### Error: "Authorization header must contain two space-delimited values"

**Causa**: Header mal formado  
**Solución**: Usar formato `Authorization: Bearer <token>`

---

**Nota**: Esta configuración está preparada para consumo de React Native en el futuro.
