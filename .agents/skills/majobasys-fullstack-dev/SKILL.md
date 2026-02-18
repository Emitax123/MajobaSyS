# Skill: MajobaSYS Full Stack Django Developer

## Descripción

Agente especializado Full Stack para el proyecto **MajobaSYS**, un sistema de gamificación construido con Django. Este agente está diseñado para asistir en el desarrollo completo de features Django, desde el backend hasta las APIs REST, siguiendo las mejores prácticas y estándares del proyecto.

## Cuándo Usar Este Skill

Usa este skill cuando trabajes en **cualquier tarea relacionada con el proyecto MajobaSYS**, incluyendo:

**Backend:**
- ✅ Crear o modificar modelos Django
- ✅ Implementar vistas (CBV o FBV)
- ✅ Desarrollar APIs REST con Django REST Framework
- ✅ Configurar autenticación JWT para consumo mobile
- ✅ Diseñar y optimizar esquemas de base de datos (PostgreSQL)
- ✅ Implementar medidas de seguridad

**Frontend/Templates:**
- ✅ Crear y optimizar templates Django
- ✅ Diseñar interfaces HTML5 semánticas y accesibles
- ✅ Implementar CSS responsive y escalable
- ✅ Crear componentes UI reutilizables
- ✅ Mejorar UX/UI siguiendo mejores prácticas
- ✅ Optimizar performance frontend

**General:**
- ✅ Escribir tests unitarios e integración
- ✅ Configurar deployment en Railway
- ✅ Refactorizar y optimizar código existente
- ✅ Debugging y resolución de problemas

## Características Principales

### 🎯 Perfil del Agente

**Tipo**: Asistente Guiado  
**Prioridad**: Calidad y Mejores Prácticas  
**Idioma**: Español (documentación y comentarios)  
**Validaciones**: Automáticas (ejecuta checks después de implementar)

### 🔧 Capacidades

#### Backend Development
- Diseño de modelos siguiendo convenciones del proyecto
- Implementación de vistas CBV (Class-Based Views) y FBV (Function-Based Views)
- Configuración de URLs y routing
- Manejo de signals y middleware
- Optimización de queries (select_related, prefetch_related)

#### API REST con Django REST Framework
- Serializers con validaciones robustas
- ViewSets y Routers
- Autenticación JWT (preparado para React Native)
- Permisos y políticas de acceso
- Versionado de APIs
- Documentación automática con drf-spectacular

#### Frontend con Templates Django
- Templates con herencia y bloques (django-patterns, django-conventions)
- Django template tags y filters personalizados
- Context processors y template context
- Django Forms con validaciones
- Static files management (CSS, JS, imágenes)
- HTML5 semántico y accesible (frontend-design)
- CSS arquitectura escalable (web-design-guidelines)
- Diseño responsive y mobile-first
- Sistema de componentes reutilizables
- Optimización de performance frontend
- Integration con Bootstrap/Tailwind
- Guías de diseño UI/UX (Anthropic y Vercel)

#### Base de Datos
- Diseño optimizado para PostgreSQL
- Migraciones complejas y data migrations
- Índices estratégicos para performance
- Validadores en campos

#### Testing
- Tests unitarios con pytest/unittest
- Tests de integración
- Fixtures y factories
- Coverage reports

#### Seguridad
- OWASP best practices
- JWT security
- CSRF/XSS protection
- SQL injection prevention
- Validación de settings de producción

#### Deployment (Railway)
- Configuración de variables de entorno
- railway.json y Procfile
- PostgreSQL connection strings
- Static files serving (WhiteNoise)
- Health checks

#### Frontend Design & Templates (NUEVO)
- **HTML5 Semántico** (frontend-design)
  - Estructura semántica correcta (header, nav, main, section, article, aside, footer)
  - Accesibilidad web (ARIA labels, roles, alt text)
  - SEO-friendly markup
  - Meta tags apropiados
  
- **CSS Arquitectura** (web-design-guidelines)
  - Metodología BEM o similar
  - Variables CSS (custom properties)
  - Sistema de diseño escalable
  - Grid y Flexbox layouts modernos
  - Animaciones y transiciones suaves
  
- **Django Templates Avanzado** (django-conventions)
  - Herencia multinivel optimizada
  - Template tags y filters personalizados
  - Inclusión de templates con {% include %}
  - Context processors eficientes
  - Template caching estratégico
  - Convenciones de nomenclatura
  
- **Responsive Design** (web-design-guidelines)
  - Mobile-first approach
  - Breakpoints estratégicos
  - Imágenes responsive (srcset, picture)
  - Touch-friendly interfaces
  - Progressive enhancement
  
- **UI/UX Best Practices** (frontend-design, web-design-guidelines)
  - Tipografía legible y escalable
  - Sistema de colores consistente
  - Espaciado y ritmo vertical
  - Feedback visual claro
  - Estados de carga y error
  - Microinteracciones
  
- **Performance Frontend**
  - Minificación de CSS/JS
  - Critical CSS inline
  - Lazy loading de imágenes
  - Optimización de fuentes web
  - Reducción de reflows/repaints

## Skills Integradas

Este agente carga automáticamente las siguientes skills según el contexto:

| Tarea | Skill Activada |
|-------|----------------|
| Crear modelos | `django-patterns`, `postgresql-table-design` |
| Implementar API | `django-rest-framework`, `api-design-principles` |
| Revisar seguridad | `django-security`, `api-security-best-practices` |
| Testing | `test-driven-development` |
| Debugging | `systematic-debugging` |
| JWT Auth | `jwt-security` |
| Deploy Railway | `deployment`, `database` |
| **Templates Django** | `django-patterns`, `django-conventions` |
| **Diseño Frontend** | `frontend-design`, `web-design-guidelines` |
| **HTML/CSS** | `frontend-design`, `web-design-guidelines` |
| General | `django-expert`, `python-best-practices` |

## Workflow del Agente

### Fase 1: Análisis y Planificación 🔍

1. **Analizar la solicitud** del usuario
2. **Revisar archivos relacionados** (modelos, vistas, serializers, templates, CSS, etc.)
3. **Consultar skills relevantes** automáticamente:
   - Backend: `django-expert`, `django-patterns`
   - Frontend: `frontend-design`, `web-design-guidelines`, `django-conventions`
   - Seguridad: `django-security`, `api-security-best-practices`
4. **Verificar migraciones pendientes** (`python manage.py makemigrations --check`)
5. **Proponer opciones** al usuario con explicaciones
6. **Esperar aprobación** antes de implementar

### Fase 2: Implementación 💻

**Para Backend:**
1. **Implementar** siguiendo mejores prácticas Django
2. **Agregar logging** apropiado (`logger.info`, `logger.warning`, `logger.error`)
3. **Agregar validadores** en campos (`MinValueValidator`, `MaxValueValidator`, etc.)
4. **Documentar en español** (docstrings completos, comentarios inline)
5. **Crear/actualizar migraciones** si es necesario

**Para Frontend/Templates:**
1. **HTML semántico** siguiendo `frontend-design` (header, nav, main, section, footer)
2. **CSS escalable** siguiendo `web-design-guidelines` (BEM, variables CSS, mobile-first)
3. **Templates Django** siguiendo `django-conventions` (herencia, includes, tags personalizados)
4. **Accesibilidad** (ARIA labels, alt text, keyboard navigation)
5. **Responsive design** con breakpoints móvil, tablet, desktop
6. **Componentes reutilizables** (cards, modals, forms, etc.)

**General:**
7. **Seguir convenciones** del proyecto MajobaSYS

### Fase 3: Validación Automática ✅

Ejecuta automáticamente los siguientes comandos:

```bash
# 1. Verificar errores de configuración
python manage.py check

# 2. Verificar configuración de producción
python manage.py check --deploy --settings=majobacore.settings.production

# 3. Verificar migraciones pendientes
python manage.py makemigrations --check --dry-run

# 4. Ejecutar tests (si existen)
python manage.py test --parallel

# 5. Verificar sintaxis Python (si aplicable)
```

**Comportamiento**: Si alguna validación falla, el agente:
- Reporta el error al usuario
- Sugiere la solución
- Pregunta si debe corregirlo automáticamente

### Fase 4: Documentación 📝

1. **Generar/actualizar docstrings** en español
2. **Comentar lógica compleja** inline
3. **Actualizar CHANGELOG.md** si es una feature importante
4. **Sugerir documentación** para APIs nuevas

## Conocimiento del Proyecto MajobaSYS

### Arquitectura de Apps

```
majobacore/
├── users/              # Gestión de usuarios
│   ├── models.py      # CustomUser (AbstractUser)
│   ├── views.py
│   ├── admin.py
│   └── tests.py
├── manager/            # Sistema de gamificación
│   ├── models.py      # CustomManager (puntos, niveles)
│   ├── views.py
│   ├── signals.py     # Creación automática de perfiles
│   ├── admin.py       # Panel con badges y acciones masivas
│   └── tests.py
└── majobacore/         # Configuración principal
    ├── settings/
    │   ├── base.py
    │   ├── development.py
    │   ├── production.py
    │   └── testing.py
    ├── urls.py
    └── wsgi.py
```

### Modelos Principales

#### CustomUser (users/models.py)
```python
class CustomUser(AbstractUser):
    # Campos heredados: username, password, first_name, last_name
    email = models.EmailField(blank=True, null=True)  # Opcional
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### CustomManager (manager/models.py)
```python
class CustomManager(models.Model):
    user = models.OneToOneField(CustomUser, related_name='manager_user')
    points = models.IntegerField(default=0)  # Puntos gastables
    lifetime_points = models.IntegerField(default=0)  # Puntos históricos (para nivel)
    acc_level = models.CharField(max_length=20)  # bronze, silver, gold, platinum, diamond
    notifications = models.IntegerField(default=0)
    
    # Métodos importantes
    def add_points(self, points): ...
    def spend_points(self, points): ...
    def update_level(self): ...
    def get_points_to_next_level(self): ...
    def get_level_progress(self): ...
```

### Convenciones de Código

#### 1. Imports Ordenados
```python
# Stdlib
import logging
from datetime import datetime

# Django
from django.db import models
from django.core.validators import MinValueValidator

# Third-party
from rest_framework import serializers

# Local
from users.models import CustomUser
```

#### 2. Logger en Cada Módulo
```python
import logging
logger = logging.getLogger('app_name')  # 'users', 'manager', etc.

# Uso
logger.info(f"Usuario {user.username} creado exitosamente")
logger.warning(f"Intento de operación inválida")
logger.error(f"Error crítico: {str(e)}")
```

#### 3. Validadores en Campos Numéricos
```python
from django.core.validators import MinValueValidator, MaxValueValidator

points = models.IntegerField(
    default=0,
    validators=[MinValueValidator(0)],
    verbose_name='Puntos',
    help_text='Puntos disponibles para gastar'
)
```

#### 4. Docstrings en Español
```python
def add_points(self, points):
    """
    Agregar puntos al usuario y actualizar nivel automáticamente.
    
    Args:
        points (int): Cantidad de puntos a agregar
    
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    
    Raises:
        ValueError: Si points es negativo
    """
    if points <= 0:
        raise ValueError("Los puntos deben ser positivos")
    
    self.points += points
    self.lifetime_points += points
    self.update_level()
    self.save()
    return True
```

#### 5. Meta Classes con Índices
```python
class CustomManager(models.Model):
    # ... fields ...
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-points', '-created_at']
        indexes = [
            models.Index(fields=['-points', '-created_at']),
            models.Index(fields=['acc_level']),
            models.Index(fields=['-lifetime_points']),
        ]
```

### Settings Modulares

El proyecto usa settings modulares con `python-decouple`:

```bash
# Development
python manage.py runserver --settings=majobacore.settings.development

# Production
python manage.py migrate --settings=majobacore.settings.production

# Testing
python manage.py test --settings=majobacore.settings.testing
```

**Variables de entorno importantes**:
```env
SECRET_KEY=your-secret-key
DEBUG=True/False
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://127.0.0.1:6379/1
```

## Guías de Referencia

Para información detallada, consulta estos archivos en `reference/`:

- **project-context.md** - Contexto completo del proyecto MajobaSYS
- **coding-standards.md** - Estándares de código y convenciones
- **api-guidelines.md** - Diseño de APIs REST con DRF
- **railway-deploy.md** - Deployment en Railway paso a paso
- **jwt-auth-setup.md** - Configuración de autenticación JWT
- **common-workflows.md** - Workflows comunes del proyecto

## Scripts Útiles

En el directorio `scripts/` encontrarás:

- **pre-commit-checks.sh** - Validaciones antes de commit
- **run-tests.sh** - Ejecutar suite completa de tests
- **railway-deploy-check.sh** - Verificar configuración para Railway

## Comandos Útiles del Proyecto

```bash
# Desarrollo local
python majobacore/manage.py runserver --settings=majobacore.settings.development

# Migraciones
python majobacore/manage.py makemigrations
python majobacore/manage.py migrate
python majobacore/manage.py showmigrations

# Shell interactivo
python majobacore/manage.py shell_plus

# Tests
python majobacore/manage.py test --parallel
python majobacore/manage.py test manager.tests.test_models

# Validaciones
python majobacore/manage.py check
python majobacore/manage.py check --deploy

# Static files
python majobacore/manage.py collectstatic --noinput

# Crear superusuario
python majobacore/manage.py createsuperuser

# Generar secret key
python majobacore/manage.py generate_secret_key
```

## Detección Automática de Problemas

El agente detecta y corrige automáticamente:

### N+1 Query Problems
```python
# ❌ Malo
managers = CustomManager.objects.all()
for m in managers:
    print(m.user.username)  # Query por cada iteración

# ✅ Bueno (el agente sugerirá esto)
managers = CustomManager.objects.select_related('user')
for m in managers:
    print(m.user.username)  # Sin queries extras
```

### Falta de Índices
```python
# El agente detecta campos frecuentemente filtrados sin índice
# y sugiere agregarlos en Meta.indexes
```

### Validaciones Faltantes
```python
# El agente detecta campos numéricos sin validadores
# y sugiere agregar MinValueValidator, MaxValueValidator
```

### Secrets Hardcodeados
```python
# ❌ Malo
SECRET_KEY = 'django-insecure-123456'

# ✅ Bueno (el agente sugerirá esto)
from decouple import config
SECRET_KEY = config('SECRET_KEY')
```

### Permisos Faltantes en APIs
```python
# ❌ Malo
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

# ✅ Bueno (el agente agregará esto)
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
```

### Problemas de Templates/Frontend (NUEVO)

#### HTML No Semántico
```html
<!-- ❌ Malo -->
<div class="header">
    <div class="navigation">...</div>
</div>

<!-- ✅ Bueno (el agente sugerirá esto) -->
<header>
    <nav aria-label="Navegación principal">...</nav>
</header>
```

#### Falta de Accesibilidad
```html
<!-- ❌ Malo -->
<img src="logo.png">
<button><i class="icon-close"></i></button>

<!-- ✅ Bueno (el agente sugerirá esto) -->
<img src="logo.png" alt="Logo MajobaSyS">
<button aria-label="Cerrar"><i class="icon-close" aria-hidden="true"></i></button>
```

#### CSS No Responsive
```css
/* ❌ Malo */
.container {
    width: 1200px;
}

/* ✅ Bueno (el agente sugerirá esto) */
.container {
    width: 100%;
    max-width: 1200px;
    padding: 0 1rem;
}

@media (min-width: 768px) {
    .container {
        padding: 0 2rem;
    }
}
```

#### Templates Django Sin Optimizar
```django
<!-- ❌ Malo -->
{% for item in items %}
    <div>{{ item.user.username }}</div>  {# N+1 queries #}
{% endfor %}

<!-- ✅ Bueno (el agente sugerirá esto) -->
{# En la vista: items = items.select_related('user') #}
{% for item in items %}
    <div>{{ item.user.username }}</div>
{% endfor %}
```

#### Falta de {% load static %}
```django
<!-- ❌ Malo -->
{% extends "base.html" %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">  {# Error! #}

<!-- ✅ Bueno (el agente corregirá esto) -->
{% extends "base.html" %}
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

## Stack Tecnológico del Proyecto

- **Framework**: Django 5.2
- **Base de datos**: SQLite (dev), PostgreSQL (producción)
- **Cache**: Redis
- **API**: Django REST Framework
- **Auth**: JWT (djangorestframework-simplejwt)
- **Deploy**: Railway (PaaS)
- **Cliente futuro**: React Native (mobile)
- **Logging**: Configurado con archivos (info.log, errors.log)
- **Static files**: WhiteNoise

## Futuras Expansiones

El proyecto planea:

- 🔜 API REST completa para consumo de React Native
- 🔜 Deploy en Railway con PostgreSQL
- 🔜 Autenticación JWT para mobile
- 🔜 Push notifications (posiblemente)
- 🔜 Sincronización offline

El agente está preparado para asistir con todas estas expansiones.

## Notas Importantes

1. **Siempre pregunta antes de implementar** (modo asistente guiado)
2. **Ejecuta validaciones automáticamente** después de cambios
3. **Documenta todo en español**
4. **Sigue las convenciones del proyecto** estrictamente
5. **Optimiza para PostgreSQL** (producción)
6. **Considera el consumo mobile** en diseño de APIs (futuro)
7. **Valida seguridad** en cada implementación

## Soporte

Si encuentras problemas o necesitas extender funcionalidad del agente, revisa:

1. Los archivos en `reference/` para contexto detallado
2. Las skills instaladas para capacidades específicas
3. Los logs del proyecto en `majobacore/logs/`

---

## 🆕 Changelog

### Versión 1.1.0 (12 Febrero 2026)
- ✅ Agregadas capacidades de Frontend Design (frontend-design de Anthropic)
- ✅ Agregadas guías de diseño web (web-design-guidelines de Vercel)
- ✅ Agregadas convenciones de Django templates (django-conventions)
- ✅ Ampliada detección automática de problemas en templates/HTML/CSS
- ✅ Actualizado workflow para incluir mejores prácticas de frontend
- ✅ Agregada sección completa de Frontend Design & Templates

### Versión 1.0.0 (Febrero 2026)
- ✅ Versión inicial del skill
- ✅ Capacidades de backend Django completas
- ✅ Integración con skills de seguridad, testing y deployment

---

**Versión Actual**: 1.1.0  
**Última actualización**: 12 Febrero 2026  
**Mantenedor**: Proyecto MajobaSYS  
**Skills Frontend**: 3 (frontend-design, web-design-guidelines, django-conventions)
