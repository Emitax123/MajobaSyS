"""
Development settings for MajobaCore project.
"""

from .base import *

# Override base settings for development
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database for development (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend para desarrollo — configurable desde .env
# Por defecto console (no envía mails reales), pero se puede cambiar a smtp en .env
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Disable cache in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Disable security features for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Session configuration for development 
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_NAME = 'majobacore_sessionid'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Logging for development — solo WARNING y errores para no ensuciar la consola,
# excepto 'api' y 'users' que se mantienen en INFO para poder ver logs de login.
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['django.request']['level'] = 'ERROR'
LOGGING['loggers']['django.security']['level'] = 'WARNING'
LOGGING['loggers']['django.db.backends']['level'] = 'WARNING'
LOGGING['loggers']['majobacore']['level'] = 'WARNING'
LOGGING['loggers']['users']['level'] = 'INFO'
LOGGING['loggers']['manager']['level'] = 'WARNING'
LOGGING['loggers']['api']['level'] = 'INFO'

# Static files configuration for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ============================================================================
# REST FRAMEWORK (Development overrides)
# ============================================================================
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/minute',
    'user': '500/minute',
    'login': '20/minute',
}

# CORS para desarrollo local de la app móvil
CORS_ALLOW_ALL_ORIGINS = True  # Solo en desarrollo
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
