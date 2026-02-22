"""
Django management command to validate production settings.

Usage:
    python manage.py check_production_settings
    python manage.py check_production_settings --settings=majobacore.settings.production
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core import checks
import sys


class Command(BaseCommand):
    help = 'Valida que la configuración de producción sea segura y completa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Modo estricto - falla si hay advertencias',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('🔍 Validando Configuración de Producción'))
        self.stdout.write('')
        
        strict_mode = options['strict']
        errors = []
        warnings = []
        success = []
        
        # ============================================================================
        # SEGURIDAD CRÍTICA
        # ============================================================================
        
        self.stdout.write(self.style.MIGRATE_LABEL('🔒 SEGURIDAD CRÍTICA'))
        
        # SECRET_KEY
        if not settings.SECRET_KEY:
            errors.append('SECRET_KEY no está configurado')
        elif 'django-insecure' in settings.SECRET_KEY:
            errors.append('SECRET_KEY contiene "django-insecure" - DEBE ser cambiado en producción')
        elif len(settings.SECRET_KEY) < 50:
            warnings.append('SECRET_KEY es muy corto (mínimo 50 caracteres recomendado)')
        else:
            success.append('SECRET_KEY configurado correctamente')
        
        # DEBUG
        if settings.DEBUG:
            errors.append('DEBUG está en True - CRÍTICO: DEBE ser False en producción')
        else:
            success.append('DEBUG está en False')
        
        # ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS:
            errors.append('ALLOWED_HOSTS está vacío')
        elif settings.ALLOWED_HOSTS == ['*']:
            errors.append('ALLOWED_HOSTS contiene "*" - inseguro en producción')
        else:
            success.append(f'ALLOWED_HOSTS configurado: {", ".join(settings.ALLOWED_HOSTS)}')
        
        # ============================================================================
        # HTTPS Y COOKIES
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('🔐 HTTPS Y COOKIES'))
        
        # SSL
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            warnings.append('SECURE_SSL_REDIRECT no está habilitado')
        else:
            success.append('SECURE_SSL_REDIRECT habilitado')
        
        # HSTS
        hsts_seconds = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
        if hsts_seconds == 0:
            warnings.append('SECURE_HSTS_SECONDS no está configurado')
        elif hsts_seconds < 31536000:
            warnings.append(f'SECURE_HSTS_SECONDS es {hsts_seconds} (recomendado: 31536000 = 1 año)')
        else:
            success.append(f'SECURE_HSTS_SECONDS configurado: {hsts_seconds}')
        
        # Cookies seguras
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            errors.append('SESSION_COOKIE_SECURE no está habilitado')
        else:
            success.append('SESSION_COOKIE_SECURE habilitado')
        
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            errors.append('CSRF_COOKIE_SECURE no está habilitado')
        else:
            success.append('CSRF_COOKIE_SECURE habilitado')
        
        if not getattr(settings, 'SESSION_COOKIE_HTTPONLY', True):
            warnings.append('SESSION_COOKIE_HTTPONLY debería estar habilitado')
        else:
            success.append('SESSION_COOKIE_HTTPONLY habilitado')
        
        # ============================================================================
        # BASE DE DATOS
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('💾 BASE DE DATOS'))
        
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'sqlite' in db_engine.lower():
            warnings.append('Usando SQLite - NO recomendado para producción')
        elif 'postgresql' in db_engine.lower():
            success.append(f'Usando PostgreSQL')
            
            # Verificar SSL
            db_options = settings.DATABASES['default'].get('OPTIONS', {})
            if db_options.get('sslmode') == 'require':
                success.append('SSL habilitado para PostgreSQL')
            else:
                warnings.append('SSL no está habilitado para PostgreSQL')
            
            # Verificar connection pooling
            if settings.DATABASES['default'].get('CONN_MAX_AGE', 0) > 0:
                success.append(f"Connection pooling habilitado: {settings.DATABASES['default']['CONN_MAX_AGE']}s")
            else:
                warnings.append('CONN_MAX_AGE no está configurado (recomendado para performance)')
        else:
            success.append(f'Base de datos: {db_engine}')
        
        # ============================================================================
        # CACHE
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('⚡ CACHE'))
        
        cache_backend = settings.CACHES['default']['BACKEND']
        
        if 'dummy' in cache_backend.lower():
            warnings.append('Usando DummyCache - NO recomendado para producción')
        elif 'redis' in cache_backend.lower():
            success.append('Cache con Redis configurado')
        else:
            success.append(f'Cache backend: {cache_backend}')
        
        # ============================================================================
        # ARCHIVOS ESTÁTICOS
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('📦 ARCHIVOS ESTÁTICOS'))
        
        if hasattr(settings, 'STATICFILES_STORAGE'):
            storage = settings.STATICFILES_STORAGE
            if 'whitenoise' in storage.lower():
                success.append('WhiteNoise configurado para archivos estáticos')
            else:
                success.append(f'Storage: {storage}')
        
        if not hasattr(settings, 'STATIC_ROOT') or not settings.STATIC_ROOT:
            warnings.append('STATIC_ROOT no está configurado')
        else:
            success.append(f'STATIC_ROOT configurado')
        
        # ============================================================================
        # EMAIL
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('📧 EMAIL'))
        
        email_backend = settings.EMAIL_BACKEND
        
        if 'console' in email_backend.lower():
            warnings.append('Email backend es ConsoleEmailBackend - solo para desarrollo')
        elif 'smtp' in email_backend.lower():
            success.append('Email backend SMTP configurado')
            
            if settings.EMAIL_HOST:
                success.append(f'Email host: {settings.EMAIL_HOST}')
            else:
                warnings.append('EMAIL_HOST no está configurado')
        else:
            success.append(f'Email backend: {email_backend}')
        
        # ============================================================================
        # LOGGING
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('📝 LOGGING'))
        
        if hasattr(settings, 'LOGGING'):
            success.append('Logging configurado')
            
            # Verificar que hay handlers configurados
            handlers = settings.LOGGING.get('handlers', {})
            if handlers:
                success.append(f'{len(handlers)} handlers de logging configurados')
            else:
                warnings.append('No hay handlers de logging configurados')
        else:
            warnings.append('LOGGING no está configurado')
        
        # ============================================================================
        # SEGURIDAD ADICIONAL
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('🛡️ SEGURIDAD ADICIONAL'))
        
        security_checks = [
            ('SECURE_CONTENT_TYPE_NOSNIFF', True, 'Protección contra MIME sniffing'),
            ('SECURE_BROWSER_XSS_FILTER', True, 'Filtro XSS del navegador'),
            ('X_FRAME_OPTIONS', 'DENY', 'Protección contra clickjacking'),
        ]
        
        for setting_name, expected_value, description in security_checks:
            actual_value = getattr(settings, setting_name, None)
            if actual_value == expected_value or (expected_value is True and actual_value):
                success.append(f'{setting_name}: {description}')
            else:
                warnings.append(f'{setting_name} no está configurado correctamente')
        
        # ============================================================================
        # MIDDLEWARE
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_LABEL('🔧 MIDDLEWARE'))
        
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ]
        
        for middleware in required_middleware:
            if middleware in settings.MIDDLEWARE:
                success.append(f'✓ {middleware.split(".")[-1]}')
            else:
                errors.append(f'Middleware faltante: {middleware}')
        
        # ============================================================================
        # RESUMEN
        # ============================================================================
        
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('=' * 80))
        self.stdout.write(self.style.MIGRATE_HEADING('📊 RESUMEN'))
        self.stdout.write('')
        
        # Mostrar éxitos
        if success:
            self.stdout.write(self.style.SUCCESS(f'✅ {len(success)} configuraciones correctas:'))
            for item in success:
                self.stdout.write(self.style.SUCCESS(f'   ✓ {item}'))
            self.stdout.write('')
        
        # Mostrar advertencias
        if warnings:
            self.stdout.write(self.style.WARNING(f'⚠️  {len(warnings)} advertencias:'))
            for item in warnings:
                self.stdout.write(self.style.WARNING(f'   ! {item}'))
            self.stdout.write('')
        
        # Mostrar errores
        if errors:
            self.stdout.write(self.style.ERROR(f'❌ {len(errors)} errores críticos:'))
            for item in errors:
                self.stdout.write(self.style.ERROR(f'   ✗ {item}'))
            self.stdout.write('')
        
        # ============================================================================
        # RECOMENDACIONES
        # ============================================================================
        
        if warnings or errors:
            self.stdout.write(self.style.MIGRATE_HEADING('💡 RECOMENDACIONES'))
            self.stdout.write('')
            
            if any('SECRET_KEY' in e for e in errors + warnings):
                self.stdout.write('  1. Generar nuevo SECRET_KEY:')
                self.stdout.write('     python manage.py generate_secret_key')
                self.stdout.write('')
            
            if any('DEBUG' in e for e in errors):
                self.stdout.write('  2. Configurar DEBUG=False en variables de entorno')
                self.stdout.write('')
            
            if any('ALLOWED_HOSTS' in e for e in errors):
                self.stdout.write('  3. Configurar ALLOWED_HOSTS con tus dominios:')
                self.stdout.write('     ALLOWED_HOSTS=tudominio.com,www.tudominio.com')
                self.stdout.write('')
            
            if any('COOKIE_SECURE' in e for e in errors + warnings):
                self.stdout.write('  4. Habilitar cookies seguras:')
                self.stdout.write('     SESSION_COOKIE_SECURE=True')
                self.stdout.write('     CSRF_COOKIE_SECURE=True')
                self.stdout.write('')
        
        # ============================================================================
        # RESULTADO FINAL
        # ============================================================================
        
        self.stdout.write(self.style.MIGRATE_HEADING('=' * 80))
        
        if errors:
            self.stdout.write(self.style.ERROR('❌ CONFIGURACIÓN NO VÁLIDA PARA PRODUCCIÓN'))
            self.stdout.write(self.style.ERROR(f'   {len(errors)} errores críticos deben ser corregidos'))
            sys.exit(1)
        elif warnings and strict_mode:
            self.stdout.write(self.style.WARNING('⚠️  CONFIGURACIÓN CON ADVERTENCIAS (modo estricto)'))
            self.stdout.write(self.style.WARNING(f'   {len(warnings)} advertencias encontradas'))
            sys.exit(1)
        elif warnings:
            self.stdout.write(self.style.WARNING('⚠️  CONFIGURACIÓN VÁLIDA CON ADVERTENCIAS'))
            self.stdout.write(self.style.WARNING(f'   {len(warnings)} advertencias - considerar corregir'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ CONFIGURACIÓN DE PRODUCCIÓN VÁLIDA'))
            self.stdout.write(self.style.SUCCESS('   Todas las validaciones pasaron correctamente'))
        
        self.stdout.write('')
