"""
Production settings for MajobaCore project.
Optimized for Railway deployment with PostgreSQL and Redis.
"""

from .base import *
import os
import sys
import logging
import dj_database_url

# ============================================================================
# DETECCIÓN DE FASE DE BUILD
# ============================================================================

# Detectar si estamos en fase de build (collectstatic) o runtime (servidor)
# Durante build, muchas variables de entorno no existen aún
IS_BUILD_PHASE = sys.argv and any(arg in sys.argv for arg in ['collectstatic', 'compress'])

# ============================================================================
# SEGURIDAD CRÍTICA
# ============================================================================

# DEBUG debe estar SIEMPRE en False en producción
DEBUG = False

# Validar que SECRET_KEY esté configurado (solo en runtime)
if not IS_BUILD_PHASE:
    INSECURE_KEYS = [
        'django-insecure-d*xd59=w7923dsnt#xy=8jbuf_c*6scivaft%ko(8r8vq6jd0l',
        'django-insecure-build-key-only-for-collectstatic',
    ]
    if not SECRET_KEY or SECRET_KEY in INSECURE_KEYS:
        import warnings
        warnings.warn(
            "SECRET_KEY must be set in environment variables for production. "
            "Generate one with: python manage.py generate_secret_key",
            RuntimeWarning
        )

# ALLOWED_HOSTS debe ser explícitamente configurado (solo en runtime)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
if not IS_BUILD_PHASE and (not ALLOWED_HOSTS or ALLOWED_HOSTS == ['localhost', '127.0.0.1']):
    import warnings
    warnings.warn(
        "ALLOWED_HOSTS must be set in environment variables for production",
        RuntimeWarning
    )

# Agregar dominio de Railway automáticamente si existe
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')
if RAILWAY_STATIC_URL and isinstance(ALLOWED_HOSTS, list):
    railway_domain = RAILWAY_STATIC_URL.replace('https://', '').replace('http://', '')
    if railway_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_domain)

# ============================================================================
# SEGURIDAD HTTP
# ============================================================================

# SSL/HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ============================================================================
# COOKIES SEGUROS
# ============================================================================

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 3600  # 1 hora para mayor seguridad
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ============================================================================
# BASE DE DATOS - POSTGRESQL
# ============================================================================

# Durante build, usar configuración dummy; en runtime, usar DATABASE_URL
if IS_BUILD_PHASE:
    # Configuración dummy para collectstatic (no se usa en build)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    # Configuración real de PostgreSQL usando DATABASE_URL (Railway lo provee automáticamente)
    # Railway format: postgresql://user:password@host:port/dbname
    DATABASE_URL = config('DATABASE_URL', default='')
    
    if not DATABASE_URL:
        import warnings
        warnings.warn(
            "DATABASE_URL not found in environment variables.\n"
            "Railway should provide this automatically when you add a PostgreSQL database.\n"
            "Format: postgresql://user:password@host:port/dbname\n"
            "Falling back to SQLite for now.",
            RuntimeWarning
        )
        # Fallback a SQLite si no hay DATABASE_URL
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    else:
        # Parse DATABASE_URL con dj-database-url
        DATABASES = {
            'default': dj_database_url.parse(
                DATABASE_URL,
                conn_max_age=600,  # Connection pooling: mantener conexiones 10 minutos
                conn_health_checks=True,  # Health checks automáticos
                ssl_require=True,  # Railway requiere SSL
            )
        }
    
        # Configuraciones adicionales de PostgreSQL
        DATABASES['default']['ATOMIC_REQUESTS'] = True  # Transacciones automáticas
        DATABASES['default']['OPTIONS'] = {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 segundos timeout para queries
        }

# ============================================================================
# CACHE - REDIS
# ============================================================================

# Durante build, usar DummyCache; en runtime, usar Redis
if IS_BUILD_PHASE:
    # Cache dummy para build
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    # Configuración real de Redis para runtime
    # Railway provee REDIS_URL automáticamente cuando agregas Redis
    REDIS_URL = config('REDIS_URL', default='')
    
    if REDIS_URL:
        # Redis configurado: usar django-redis
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': REDIS_URL,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'SOCKET_CONNECT_TIMEOUT': 5,
                    'SOCKET_TIMEOUT': 5,
                    'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                    'CONNECTION_POOL_KWARGS': {
                        'max_connections': 50,
                        'retry_on_timeout': True,
                    },
                    'IGNORE_EXCEPTIONS': True,  # No fallar si Redis no está disponible
                },
                'KEY_PREFIX': 'majobasys',
                'TIMEOUT': 300,  # 5 minutos por defecto
            }
        }
    else:
        # Redis no configurado: usar cache local (menos eficiente pero funciona)
        import warnings
        warnings.warn(
            "REDIS_URL not found - using LocMemCache. "
            "For better performance, add Redis in Railway.",
            RuntimeWarning
        )
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        }

# Session backend con Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ============================================================================
# ARCHIVOS ESTÁTICOS
# ============================================================================

# WhiteNoise para servir archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Compresión de archivos estáticos
WHITENOISE_COMPRESSION_QUALITY = 90
WHITENOISE_MAX_AGE = 31536000  # 1 año de cache
WHITENOISE_MANIFEST_STRICT = False  # No fallar si falta un archivo

# ============================================================================
# ARCHIVOS MEDIA (Opcional: S3)
# ============================================================================

# Si se usa S3 para archivos media, descomentar:
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Usar almacenamiento local
    MEDIA_ROOT = BASE_DIR / 'media'
    MEDIA_URL = '/media/'

# ============================================================================
# EMAIL
# ============================================================================

# ============================================================================
# EMAIL
# ============================================================================

# Configuración de email (opcional durante build, con defaults en runtime)
if IS_BUILD_PHASE:
    # Durante build, usar console backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Durante runtime: Si EMAIL_HOST está configurado, usar SMTP; si no, console
    EMAIL_HOST = config('EMAIL_HOST', default='')
    
    if EMAIL_HOST:
        # SMTP configurado
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
        EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
        EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
        EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
        EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
        DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@majobacore.com')
        SERVER_EMAIL = config('SERVER_EMAIL', default='admin@majobacore.com')
        
        # Administradores que reciben emails de errores
        ADMINS = [
            ('Admin', config('ADMIN_EMAIL', default=SERVER_EMAIL)),
        ]
        MANAGERS = ADMINS
    else:
        # Email no configurado: usar console backend (logs en stdout)
        import warnings
        warnings.warn(
            "EMAIL_HOST not configured - emails will be printed to console. "
            "Configure SMTP settings for production email delivery.",
            RuntimeWarning
        )
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        DEFAULT_FROM_EMAIL = 'noreply@majobacore.com'
        SERVER_EMAIL = 'admin@majobacore.com'
        ADMINS = []
        MANAGERS = []

# ============================================================================
# LOGGING PARA PRODUCCIÓN
# ============================================================================

# Sobrescribir configuración de logging para producción
LOGGING['formatters']['json'] = {
    '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
    'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s',
}

# Handler para stdout (Railway captura esto)
LOGGING['handlers']['console_json'] = {
    'level': 'INFO',
    'class': 'logging.StreamHandler',
    'formatter': 'json',
    'stream': sys.stdout,
}

# Actualizar loggers para producción
LOGGING['root']['handlers'] = ['console_json']
LOGGING['loggers']['django']['handlers'] = ['console_json']
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['django.request']['handlers'] = ['console_json', 'mail_admins']
LOGGING['loggers']['django.security']['handlers'] = ['console_json', 'mail_admins']
LOGGING['loggers']['majobacore']['handlers'] = ['console_json']
LOGGING['loggers']['users']['handlers'] = ['console_json']
LOGGING['loggers']['manager']['handlers'] = ['console_json']

# ============================================================================
# SEGURIDAD ADICIONAL
# ============================================================================

# Middleware de seguridad en orden correcto
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'majobacore.utils.security.SecurityHeadersMiddleware',  # Nuestro middleware personalizado
]

# Límites de carga de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ============================================================================
# DJANGO REST FRAMEWORK (si se usa)
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# ============================================================================
# MONITOREO Y ANALYTICS
# ============================================================================

# Sentry para tracking de errores
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        environment='production',
        traces_sample_rate=0.1,  # 10% de las transacciones
        profiles_sample_rate=0.1,  # 10% de los perfiles
        send_default_pii=False,  # No enviar información personal
        attach_stacktrace=True,
        before_send=lambda event, hint: event if event.get('level') != 'info' else None,
    )

# ============================================================================
# CORS (si se necesita para API)
# ============================================================================

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())
if CORS_ALLOWED_ORIGINS:
    INSTALLED_APPS += ['corsheaders']
    MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]

# ============================================================================
# OPTIMIZACIONES DE RENDIMIENTO
# ============================================================================

# Template caching - Solo si no se está en modo APP_DIRS
# APP_DIRS y loaders son mutuamente excluyentes
TEMPLATES[0]['APP_DIRS'] = False  # Deshabilitar APP_DIRS para usar loaders
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Deshabilitar template debug
TEMPLATES[0]['OPTIONS']['debug'] = False

# ============================================================================
# ADMIN PERSONALIZADO
# ============================================================================

# URL del admin (security by obscurity)
ADMIN_URL = config('ADMIN_URL', default='admin/')

# ============================================================================
# HEALTH CHECK
# ============================================================================

# django_extensions ya está incluido en base.py
# No añadir nuevamente para evitar duplicados

# ============================================================================
# VALIDACIONES FINALES
# ============================================================================

# Verificar que las configuraciones CRÍTICAS estén presentes
# Solo validar en RUNTIME, no durante BUILD
if not IS_BUILD_PHASE:
    # Validar solo las variables absolutamente necesarias
    # DATABASE_URL y REDIS_URL son opcionales (tienen fallbacks)
    RECOMMENDED_ENV_VARS = [
        'SECRET_KEY',
        'DATABASE_URL',  # Railway lo provee automáticamente
        'ALLOWED_HOSTS',
    ]

    missing_vars = [var for var in RECOMMENDED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        import warnings
        warnings.warn(
            f"Missing recommended environment variables for production:\n"
            f"  {', '.join(missing_vars)}\n\n"
            f"Railway Setup:\n"
            f"  1. Add PostgreSQL database (provides DATABASE_URL automatically)\n"
            f"  2. Set SECRET_KEY: python manage.py generate_secret_key\n"
            f"  3. Set ALLOWED_HOSTS to your Railway domain\n\n"
            f"See RAILWAY_ENV_SETUP.md for details.",
            RuntimeWarning
        )

# Log de inicio
import logging
logger = logging.getLogger('majobacore')

if IS_BUILD_PHASE:
    logger.info('Production settings loaded in BUILD PHASE (collectstatic)')
    logger.info('Using dummy configurations for database and cache')
else:
    logger.info('Production settings loaded successfully in RUNTIME')
    logger.info(f'DEBUG mode: {DEBUG}')
    logger.info(f'ALLOWED_HOSTS: {ALLOWED_HOSTS}')
    db_engine = DATABASES["default"]["ENGINE"]
    db_host = DATABASES["default"].get("HOST", "local/sqlite")
    logger.info(f'Database: {db_engine} at {db_host}')
    logger.info(f'Cache backend: {CACHES["default"]["BACKEND"]}')
