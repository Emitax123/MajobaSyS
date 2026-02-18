# Contexto del Proyecto MajobaSYS

## Visión General

**MajobaSYS** es un sistema de gamificación empresarial construido con Django que permite gestionar usuarios, asignar puntos, administrar niveles y otorgar recompensas basadas en el rendimiento.

### Objetivos del Proyecto

1. **Gamificar procesos empresariales** mediante un sistema de puntos y niveles
2. **Motivar a usuarios** a través de recompensas y rankings
3. **Proveer APIs REST** para consumo de aplicaciones móviles (React Native en el futuro)
4. **Escalar horizontalmente** con deployment en Railway
5. **Mantener seguridad robusta** con autenticación JWT

## Arquitectura del Proyecto

### Estructura de Directorios

```
MajobaSYS-1/
├── .agents/
│   └── skills/                    # Skills del proyecto
│       ├── django-expert/
│       ├── django-rest-framework/
│       ├── django-patterns/
│       ├── django-security/
│       ├── api-design-principles/
│       ├── python-best-practices/
│       ├── deployment/            # Railway deployment
│       ├── database/              # Railway database
│       ├── jwt-security/          # JWT authentication
│       ├── api-security-best-practices/
│       └── majobasys-fullstack-dev/  # Este agente
├── majobacore/                    # Proyecto Django principal
│   ├── users/                     # App de usuarios
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py             # CustomUser
│   │   ├── tests.py
│   │   └── views.py
│   ├── manager/                   # App de gamificación
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   └── 0002_add_lifetime_points_and_improvements.py
│   │   ├── __init__.py
│   │   ├── admin.py              # Panel admin con badges y acciones masivas
│   │   ├── apps.py
│   │   ├── models.py             # CustomManager (sistema de puntos)
│   │   ├── signals.py            # Creación automática de perfiles
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── majobacore/                # Configuración principal
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Settings comunes
│   │   │   ├── development.py    # Settings de desarrollo
│   │   │   ├── production.py     # Settings de producción
│   │   │   └── testing.py        # Settings de testing
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── generate_secret_key.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── security.py
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── wsgi.py
│   ├── logs/                      # Logs del sistema
│   │   ├── info.log
│   │   └── errors.log
│   ├── static/                    # Archivos estáticos
│   ├── templates/                 # Templates Django
│   ├── db.sqlite3                 # Base de datos de desarrollo
│   └── manage.py
├── .gitignore
├── MEJORAS_IMPLEMENTADAS.md       # Changelog detallado
└── README.md (futuro)
```

## Apps del Proyecto

### 1. Users App

**Responsabilidad**: Gestión de usuarios y autenticación

**Modelos**:
- `CustomUser` - Usuario personalizado sin email obligatorio

**Características**:
- Hereda de `AbstractUser`
- Email opcional (no requerido para login)
- Campos adicionales: phone, position, department
- USERNAME_FIELD = 'username'
- Logging integrado

**Ejemplo de uso**:
```python
from users.models import CustomUser

# Crear usuario
user = CustomUser.objects.create_user(
    username='juan_perez',
    password='password123',
    first_name='Juan',
    last_name='Pérez',
    position='Desarrollador',
    department='IT'
)
```

### 2. Manager App

**Responsabilidad**: Sistema de gamificación (puntos, niveles, notificaciones)

**Modelos**:
- `CustomManager` - Perfil de gamificación vinculado a cada usuario

**Características**:
- Relación OneToOne con CustomUser
- Sistema de puntos (actuales y lifetime)
- 5 niveles: Bronze, Silver, Gold, Platinum, Diamond
- Métodos para agregar/gastar puntos
- Actualización automática de niveles
- Índices de base de datos para performance
- Signals para creación automática de perfiles

**Sistema de Niveles**:
| Nivel    | Puntos Lifetime | Color   |
|----------|----------------|---------|
| Bronze   | 0 - 499        | #CD7F32 |
| Silver   | 500 - 1,999    | #C0C0C0 |
| Gold     | 2,000 - 4,999  | #FFD700 |
| Platinum | 5,000 - 9,999  | #E5E4E2 |
| Diamond  | 10,000+        | #B9F2FF |

**Ejemplo de uso**:
```python
from manager.models import CustomManager

# Acceder al perfil
manager = user.manager_user

# Agregar puntos (actualiza nivel automáticamente)
manager.add_points(1000)

# Gastar puntos (no afecta nivel)
if manager.spend_points(500):
    print("Compra exitosa")

# Ver progreso
print(f"Nivel: {manager.get_acc_level_display()}")
print(f"Progreso: {manager.get_level_progress()}%")
print(f"Faltan: {manager.get_points_to_next_level()} puntos")
```

## Stack Tecnológico

### Backend
- **Framework**: Django 5.2
- **Python**: 3.11+
- **Autenticación**: Django Auth + JWT (futuro)
- **Admin**: Django Admin personalizado

### Base de Datos
- **Desarrollo**: SQLite3
- **Producción**: PostgreSQL (Railway)
- **ORM**: Django ORM
- **Migraciones**: Django Migrations

### Cache & Sessions
- **Cache**: Redis
- **Sessions**: Redis-backed sessions
- **TTL**: 24 horas

### APIs
- **Framework**: Django REST Framework (futuro)
- **Auth**: JWT con djangorestframework-simplejwt (futuro)
- **Documentación**: drf-spectacular (futuro)
- **Versionado**: URL-based (v1, v2)

### Frontend
- **Templates**: Django Template Language
- **Static files**: WhiteNoise
- **CSS**: Bootstrap/Tailwind (por definir)

### Deployment
- **Plataforma**: Railway (PaaS)
- **Web server**: Gunicorn
- **Proxy**: Railway built-in
- **Static files**: WhiteNoise
- **Database**: PostgreSQL en Railway

### Cliente Futuro
- **Mobile**: React Native
- **API consumption**: REST con JWT

### Configuración
- **Environment**: python-decouple
- **Settings**: Modulares (base, dev, prod, testing)

### Logging
- **Sistema**: Python logging
- **Archivos**:
  - `logs/info.log` - Info general
  - `logs/errors.log` - Solo errores
- **Formato**: `[timestamp] LEVEL app: message`

### Testing (Futuro)
- **Framework**: pytest + pytest-django
- **Coverage**: pytest-cov
- **Fixtures**: Factory Boy

## Flujo de Datos

### Creación de Usuario

```
1. CustomUser.objects.create_user()
   ↓
2. Signal post_save detecta creación
   ↓
3. CustomManager.objects.create(user=instance)
   ↓
4. Perfil de gamificación creado automáticamente
   - points = 0
   - lifetime_points = 0
   - acc_level = 'bronze'
```

### Sistema de Puntos

```
1. manager.add_points(100)
   ↓
2. points += 100
   lifetime_points += 100
   ↓
3. update_level() se llama automáticamente
   ↓
4. Si lifetime_points cruza umbral:
   - acc_level cambia (bronze → silver)
   - Logger registra cambio de nivel
   ↓
5. save() persiste cambios
```

### Gasto de Puntos

```
1. manager.spend_points(50)
   ↓
2. Verificar: points >= 50 ?
   ↓ Sí
3. points -= 50
   (lifetime_points NO cambia)
   ↓
4. save() persiste
   ↓
5. Nivel NO cambia (basado en lifetime_points)
```

## Configuración de Settings

### Base Settings (base.py)

Contiene configuración común a todos los ambientes:
- SECRET_KEY (desde env)
- INSTALLED_APPS
- MIDDLEWARE
- TEMPLATES
- DATABASES (configurables por env)
- AUTH_USER_MODEL = 'users.CustomUser'
- PASSWORD_VALIDATORS
- LOGGING
- CACHE (Redis)
- SESSION_ENGINE

### Development Settings (development.py)

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Production Settings (production.py)

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Variables de Entorno

### Desarrollo (.env)

```env
SECRET_KEY=django-insecure-development-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite por defecto)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Email (console en dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Producción (Railway)

```env
SECRET_KEY=generated-secure-secret-key
DEBUG=False
DJANGO_SETTINGS_MODULE=majobacore.settings.production
ALLOWED_HOSTS=*.up.railway.app,yourdomain.com

# Database (proporcionado por Railway)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis (Railway addon)
REDIS_URL=redis://host:port

# Email (configurar SMTP real)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

## Roadmap del Proyecto

### ✅ Fase 1: MVP Completado

- [x] Modelo CustomUser
- [x] Modelo CustomManager con sistema de puntos
- [x] Sistema de niveles (5 niveles)
- [x] Signals para creación automática de perfiles
- [x] Panel admin con badges y acciones masivas
- [x] Logging configurado
- [x] Migraciones completas
- [x] Settings modulares
- [x] Cache con Redis

### 🔄 Fase 2: APIs REST (En Planificación)

- [ ] Django REST Framework instalado
- [ ] Serializers para CustomUser y CustomManager
- [ ] ViewSets con CRUD completo
- [ ] Autenticación JWT configurada
- [ ] Endpoints de token (obtain, refresh)
- [ ] Permisos y políticas de acceso
- [ ] Documentación con drf-spectacular
- [ ] Tests de APIs

### 🔜 Fase 3: Deployment Railway

- [ ] railway.json configurado
- [ ] Procfile para Gunicorn
- [ ] PostgreSQL en Railway
- [ ] Variables de entorno en Railway
- [ ] Static files con WhiteNoise
- [ ] Health checks
- [ ] Logs en Railway
- [ ] CI/CD (opcional)

### 🔜 Fase 4: Cliente React Native

- [ ] Endpoints finalizados para consumo mobile
- [ ] JWT authentication flow
- [ ] Optimización de payloads para mobile
- [ ] Paginación eficiente
- [ ] Error handling estándar
- [ ] Versionado de API (v1)

### 🔜 Fase 5: Features Adicionales

- [ ] Sistema de recompensas/premios
- [ ] Achievements/Badges personalizados
- [ ] Leaderboards en tiempo real
- [ ] Notificaciones push
- [ ] Historial de transacciones
- [ ] Dashboard de analytics
- [ ] Exportación de reportes

## Decisiones de Diseño Importantes

### 1. Email Opcional en CustomUser

**Decisión**: Email no es requerido para login  
**Razón**: Usuarios creados manualmente por administradores no siempre tienen email corporativo  
**Impacto**: USERNAME_FIELD = 'username', REQUIRED_FIELDS = []

### 2. Separación points vs lifetime_points

**Decisión**: Dos campos distintos para puntos  
**Razón**: 
- `points` = puntos gastables (pueden disminuir)
- `lifetime_points` = puntos históricos (solo aumentan, determinan nivel)
**Impacto**: El nivel nunca baja aunque gastes puntos

### 3. Settings Modulares

**Decisión**: Settings divididos en base, dev, prod, testing  
**Razón**: Facilita diferentes configuraciones por ambiente sin duplicación  
**Impacto**: Comandos requieren `--settings` flag

### 4. Signals para Perfiles

**Decisión**: Usar signals post_save para crear CustomManager automáticamente  
**Razón**: Evita errores por perfiles faltantes, garantiza consistencia  
**Impacto**: Todo usuario tiene perfil garantizado

### 5. Logging a Archivos

**Decisión**: Logs se escriben a archivos, no a consola (en producción)  
**Razón**: Consola saturada en producción, archivos permiten análisis histórico  
**Impacto**: Revisar logs en `logs/info.log` y `logs/errors.log`

### 6. Cache con Redis

**Decisión**: Redis para cache y sessions  
**Razón**: Performance, escalabilidad, compartir sessions entre instancias  
**Impacto**: Requiere Redis en producción (Railway addon)

### 7. PostgreSQL en Producción

**Decisión**: SQLite en dev, PostgreSQL en prod  
**Razón**: SQLite no soporta concurrencia, PostgreSQL es estándar en producción  
**Impacto**: Considerar diferencias de SQL entre ambas

## Patrones Comunes

### Acceder al Perfil desde Usuario

```python
# Correcto
user = CustomUser.objects.get(username='juan')
manager = user.manager_user  # related_name en OneToOne

# Incorrecto
manager = CustomManager.objects.get(user__username='juan')  # Funciona pero menos eficiente
```

### Optimizar Queries

```python
# ❌ N+1 problem
managers = CustomManager.objects.all()
for m in managers:
    print(m.user.username)  # Query extra por cada uno

# ✅ Optimizado
managers = CustomManager.objects.select_related('user')
for m in managers:
    print(m.user.username)  # Sin queries extras
```

### Logging Consistente

```python
import logging
logger = logging.getLogger(__name__)

# En métodos
def add_points(self, points):
    logger.info(f"Usuario {self.user.username} ganó {points} puntos")
    # ... lógica
```

## Contacto y Soporte

**Proyecto**: MajobaSYS  
**Versión**: 1.1.0  
**Última actualización**: Febrero 2026  
**Documentación**: Ver MEJORAS_IMPLEMENTADAS.md para changelog detallado
