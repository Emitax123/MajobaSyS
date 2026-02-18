"""
Security utilities for MajobaCore project.
"""

import secrets
import string
import logging
from django.core.management.utils import get_random_secret_key
from django.conf import settings

logger = logging.getLogger('majobacore.security')


def generate_secret_key():
    """Generate a new Django secret key."""
    return get_random_secret_key()


def generate_random_password(length=12):
    """
    Generate a random secure password.
    
    Args:
        length (int): Length of the password (minimum 12)
    
    Returns:
        str: Random password
    """
    if length < 12:
        raise ValueError("Password length must be at least 12 characters")
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


class SecurityHeadersMiddleware:
    """
    Enhanced security headers middleware for production.
    
    Adds comprehensive security headers to all HTTP responses:
    - Content Security Policy (CSP)
    - XSS Protection
    - Frame Options
    - Content Type Options
    - Referrer Policy
    - Permissions Policy
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Configurar CSP según el entorno
        self.csp_directives = self._build_csp_policy()
        
        logger.info("SecurityHeadersMiddleware initialized")

    def _build_csp_policy(self):
        """
        Build Content Security Policy based on environment.
        
        Returns:
            str: CSP header value
        """
        # CSP base para producción
        directives = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",  # Necesario para Django admin
                "'unsafe-eval'",    # Solo si es necesario, idealmente remover
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",  # Necesario para estilos inline
                "https://fonts.googleapis.com",
            ],
            "font-src": [
                "'self'",
                "https://fonts.gstatic.com",
            ],
            "img-src": [
                "'self'",
                "data:",
                "https:",
            ],
            "connect-src": [
                "'self'",
            ],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "upgrade-insecure-requests": [],
        }
        
        # Si hay dominios adicionales permitidos, agregarlos
        if hasattr(settings, 'CSP_ADDITIONAL_DOMAINS'):
            for domain in settings.CSP_ADDITIONAL_DOMAINS:
                directives["script-src"].append(domain)
                directives["connect-src"].append(domain)
        
        # Construir el string de CSP
        csp_parts = []
        for directive, values in directives.items():
            if values:
                csp_parts.append(f"{directive} {' '.join(values)}")
            else:
                csp_parts.append(directive)
        
        return "; ".join(csp_parts)

    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo agregar headers a respuestas HTML/JSON
        content_type = response.get('Content-Type', '')
        
        # Content Security Policy
        if not response.get('Content-Security-Policy'):
            response['Content-Security-Policy'] = self.csp_directives
        
        # X-Content-Type-Options
        if not response.get('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options (previene clickjacking)
        if not response.get('X-Frame-Options'):
            response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection (para navegadores antiguos)
        if not response.get('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        if not response.get('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy (antes Feature-Policy)
        if not response.get('Permissions-Policy'):
            permissions = [
                'geolocation=()',
                'microphone=()',
                'camera=()',
                'payment=()',
                'usb=()',
                'magnetometer=()',
                'gyroscope=()',
                'accelerometer=()',
            ]
            response['Permissions-Policy'] = ', '.join(permissions)
        
        # Cross-Origin-Embedder-Policy
        if not response.get('Cross-Origin-Embedder-Policy'):
            response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        # Cross-Origin-Opener-Policy
        if not response.get('Cross-Origin-Opener-Policy'):
            response['Cross-Origin-Opener-Policy'] = 'same-origin'
        
        # Cross-Origin-Resource-Policy
        if not response.get('Cross-Origin-Resource-Policy'):
            response['Cross-Origin-Resource-Policy'] = 'same-origin'
        
        return response


class RateLimitMiddleware:
    """
    Simple rate limiting middleware.
    Para rate limiting más robusto, considerar django-ratelimit o django-axes.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("RateLimitMiddleware initialized")
    
    def __call__(self, request):
        # Implementar lógica de rate limiting aquí
        # Por ahora es un placeholder
        response = self.get_response(request)
        return response


# Rate limiting configuration
RATE_LIMIT_SETTINGS = {
    'DEFAULT_RATE_LIMIT': '100/hour',
    'LOGIN_RATE_LIMIT': '5/min',
    'REGISTRATION_RATE_LIMIT': '3/min',
    'PASSWORD_RESET_RATE_LIMIT': '3/hour',
    'API_RATE_LIMIT': '1000/hour',
    'SEARCH_RATE_LIMIT': '30/min',
}


# Security checklist for production deployment
PRODUCTION_SECURITY_CHECKLIST = {
    'critical': [
        "Set DEBUG = False in production",
        "Use strong SECRET_KEY (64+ characters)",
        "Configure ALLOWED_HOSTS properly",
        "Enable HTTPS (SECURE_SSL_REDIRECT = True)",
        "Set all secure cookie flags (SECURE, HTTPONLY, SAMESITE)",
        "Configure HSTS headers (min 31536000 seconds)",
        "Use environment variables for all secrets",
        "Enable database SSL connections",
    ],
    'important': [
        "Configure proper logging (JSON format for production)",
        "Set up monitoring and error tracking (Sentry)",
        "Implement rate limiting on sensitive endpoints",
        "Enable CSRF protection on all forms",
        "Validate and sanitize all user inputs",
        "Use parameterized queries (ORM)",
        "Configure file upload limits",
        "Set proper Content-Security-Policy",
    ],
    'recommended': [
        "Regular security updates of dependencies",
        "Automated backup strategy",
        "Database connection pooling",
        "Redis for caching and sessions",
        "Static file compression (WhiteNoise)",
        "Health check endpoints",
        "Monitoring and alerting",
        "Load testing before deployment",
        "DDoS protection (Cloudflare)",
        "WAF (Web Application Firewall)",
    ],
}


def validate_production_security():
    """
    Validate that production security settings are properly configured.
    
    Returns:
        tuple: (is_valid, list of issues)
    """
    issues = []
    
    # Verificar SECRET_KEY
    if not settings.SECRET_KEY or 'django-insecure' in settings.SECRET_KEY:
        issues.append("SECRET_KEY is not set or is insecure")
    
    # Verificar DEBUG
    if settings.DEBUG:
        issues.append("DEBUG is True in production (CRITICAL)")
    
    # Verificar ALLOWED_HOSTS
    if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
        issues.append("ALLOWED_HOSTS is not properly configured")
    
    # Verificar HTTPS
    if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
        issues.append("SECURE_SSL_REDIRECT is not enabled")
    
    # Verificar HSTS
    hsts_seconds = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
    if hsts_seconds < 31536000:
        issues.append(f"SECURE_HSTS_SECONDS is too low: {hsts_seconds} (should be 31536000)")
    
    # Verificar cookies seguras
    if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
        issues.append("SESSION_COOKIE_SECURE is not enabled")
    
    if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
        issues.append("CSRF_COOKIE_SECURE is not enabled")
    
    # Verificar base de datos
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'sqlite' in db_engine.lower():
        issues.append("Using SQLite in production (not recommended)")
    
    # Verificar cache
    cache_backend = settings.CACHES['default']['BACKEND']
    if 'dummy' in cache_backend.lower():
        issues.append("Using DummyCache in production")
    
    is_valid = len(issues) == 0
    
    if is_valid:
        logger.info("Production security validation: PASSED")
    else:
        logger.warning(f"Production security validation: FAILED with {len(issues)} issues")
        for issue in issues:
            logger.warning(f"  - {issue}")
    
    return is_valid, issues


def log_security_event(event_type, user=None, ip_address=None, details=None):
    """
    Log security-related events for monitoring and auditing.
    
    Args:
        event_type (str): Type of security event (login, logout, failed_login, etc.)
        user: User object or username
        ip_address (str): IP address of the request
        details (dict): Additional details about the event
    """
    log_data = {
        'event_type': event_type,
        'timestamp': str(secrets.token_urlsafe(16)),
        'ip_address': ip_address,
    }
    
    if user:
        log_data['user'] = str(user)
    
    if details:
        log_data['details'] = details
    
    logger.info(f"Security event: {event_type}", extra=log_data)
