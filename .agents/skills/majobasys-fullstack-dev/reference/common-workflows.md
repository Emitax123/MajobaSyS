# Workflows Comunes - MajobaSYS

## 1. Crear un Nuevo Modelo

### Paso 1: Definir el Modelo

```python
# app/models.py
from django.db import models
from django.core.validators import MinValueValidator
import logging

logger = logging.getLogger('app_name')

class MiModelo(models.Model):
    """Descripción del modelo."""
    
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='mis_modelos'
    )
    
    nombre = models.CharField(max_length=100)
    valor = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]
    
    def __str__(self):
        return self.nombre
```

### Paso 2: Crear Migración

```bash
python majobacore/manage.py makemigrations
python majobacore/manage.py migrate
```

### Paso 3: Registrar en Admin

```python
# app/admin.py
from django.contrib import admin
from .models import MiModelo

@admin.register(MiModelo)
class MiModeloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'valor', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['nombre', 'user__username']
```

### Paso 4: Crear Tests

```python
# app/tests.py
from django.test import TestCase

class MiModeloTestCase(TestCase):
    def test_crear_modelo(self):
        modelo = MiModelo.objects.create(nombre="Test")
        self.assertEqual(modelo.nombre, "Test")
```

## 2. Implementar API REST Completa

### Paso 1: Crear Serializer

```python
# api/serializers.py
from rest_framework import serializers

class MiModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiModelo
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
```

### Paso 2: Crear ViewSet

```python
# api/viewsets.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class MiModeloViewSet(viewsets.ModelViewSet):
    queryset = MiModelo.objects.all()
    serializer_class = MiModeloSerializer
    permission_classes = [IsAuthenticated]
```

### Paso 3: Configurar URLs

```python
# api/urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'mi-modelo', MiModeloViewSet)

urlpatterns = router.urls
```

### Paso 4: Tests de API

```python
from rest_framework.test import APITestCase

class MiModeloAPITestCase(APITestCase):
    def test_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/mi-modelo/')
        self.assertEqual(response.status_code, 200)
```

## 3. Agregar Feature al Sistema de Gamificación

### Ejemplo: Sistema de Badges/Logros

```python
# manager/models.py
class Badge(models.Model):
    """Badge/Logro que usuarios pueden desbloquear."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    points_required = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    """Relación usuario-badge (badges desbloqueados)."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']
```

## 4. Optimizar Performance

### Identificar N+1 Problems

```python
# Usar django-debug-toolbar
pip install django-debug-toolbar

# settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### Optimizar Queries

```python
# Antes (N+1)
managers = CustomManager.objects.all()
for m in managers:
    print(m.user.username)  # Query extra

# Después (optimizado)
managers = CustomManager.objects.select_related('user')
```

## 5. Implementar Caché

```python
from django.core.cache import cache

def get_top_users():
    """Obtener top 10 usuarios con caché."""
    key = 'top_users'
    data = cache.get(key)
    
    if data is None:
        data = list(CustomManager.objects.order_by('-points')[:10].values())
        cache.set(key, data, 300)  # 5 minutos
    
    return data
```

## 6. Debugging Sistemático

### Paso 1: Reproducir el Error

```python
# Crear test que reproduzca el bug
def test_bug_reproduce(self):
    # Pasos para reproducir
    manager.add_points(-100)  # Esto debería fallar
```

### Paso 2: Investigar Logs

```bash
tail -f majobacore/logs/errors.log
```

### Paso 3: Usar Debugger

```python
import pdb; pdb.set_trace()  # Breakpoint
```

### Paso 4: Fix y Verificar

```python
# Agregar validación
if points <= 0:
    raise ValueError("Puntos deben ser positivos")
```

## 7. Deploy a Railway

### Checklist Pre-Deploy

```bash
# 1. Actualizar requirements.txt
pip freeze > requirements.txt

# 2. Verificar settings de producción
python majobacore/manage.py check --deploy --settings=majobacore.settings.production

# 3. Crear migraciones pendientes
python majobacore/manage.py makemigrations

# 4. Test local con settings de producción
DEBUG=False python majobacore/manage.py runserver --settings=majobacore.settings.production

# 5. Commit y push
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Deploy

```bash
railway up
railway run python majobacore/manage.py migrate
railway run python majobacore/manage.py createsuperuser
```

## 8. Agregar Tests

### Test de Modelo

```python
from django.test import TestCase

class CustomManagerTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='test')
        self.manager = self.user.manager_user
    
    def test_add_points(self):
        self.manager.add_points(100)
        self.assertEqual(self.manager.points, 100)
```

### Test de API

```python
from rest_framework.test import APITestCase

class ManagerAPITestCase(APITestCase):
    def test_list_managers(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/managers/')
        self.assertEqual(response.status_code, 200)
```

### Ejecutar Tests

```bash
# Todos los tests
python majobacore/manage.py test

# Tests específicos
python majobacore/manage.py test manager.tests.test_models

# Con coverage
pip install coverage
coverage run --source='.' majobacore/manage.py test
coverage report
```

## 9. Refactoring Seguro

### Paso 1: Agregar Tests para Código Existente

```python
# Asegurar comportamiento actual
def test_existing_behavior(self):
    result = funcion_a_refactorizar()
    self.assertEqual(result, expected)
```

### Paso 2: Refactorizar

```python
# Mejorar código manteniendo comportamiento
def funcion_mejorada():
    # Nueva implementación más limpia
    pass
```

### Paso 3: Verificar Tests Pasan

```bash
python majobacore/manage.py test
```

## 10. Actualizar Dependencias

```bash
# Ver dependencias outdated
pip list --outdated

# Actualizar una dependencia
pip install --upgrade django

# Actualizar requirements.txt
pip freeze > requirements.txt

# Verificar que todo funciona
python majobacore/manage.py check
python majobacore/manage.py test
```

---

**Tip**: Siempre seguir el ciclo Red-Green-Refactor en TDD:
1. **Red**: Escribir test que falla
2. **Green**: Implementar mínimo para que pase
3. **Refactor**: Mejorar código manteniendo tests pasando
