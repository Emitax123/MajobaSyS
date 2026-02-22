"""
Configuración específica para testing.
Optimizada para ejecutar tests rápidos y confiables.
"""
from .base import *

# =====================================
# DEBUG
# =====================================
DEBUG = False
TEMPLATE_DEBUG = False

# =====================================
# DATABASE
# =====================================
# Base de datos en memoria para tests ultra-rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# =====================================
# PASSWORD HASHERS
# =====================================
# Hasher rápido para tests (no seguro para producción)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# =====================================
# CACHE
# =====================================
# Cache dummy (sin backend real)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# =====================================
# SESSIONS
# =====================================
# Sesiones en base de datos (en memoria)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =====================================
# EMAIL
# =====================================
# Email a consola para testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =====================================
# CELERY
# =====================================
# Ejecución síncrona de tareas Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# =====================================
# LOGGING
# =====================================
# Logging mínimo para no ensuciar output de tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'manager': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =====================================
# MIDDLEWARE
# =====================================
# Remover middlewares innecesarios para tests
MIDDLEWARE = [item for item in MIDDLEWARE if 'debug_toolbar' not in item.lower()]

# =====================================
# MIGRACIONES (Opcional - acelera tests)
# =====================================
# Deshabilitar migraciones para tests aún más rápidos
# Descomenta si quieres tests ultra-rápidos (puede causar problemas con custom fields)
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

# =====================================
# STATIC FILES
# =====================================
# No coleccionar static files durante tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =====================================
# SECURITY
# =====================================
# Deshabilitar seguridad HTTPS en tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
