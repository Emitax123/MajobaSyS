"""
Security utilities for MajobaCore project.
"""

import secrets
import string
from django.core.management.utils import get_random_secret_key


def generate_secret_key():
    """Generate a new Django secret key."""
    return get_random_secret_key()


def generate_random_password(length=12):
    """Generate a random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


# Security headers middleware
class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


# Rate limiting configuration
RATE_LIMIT_SETTINGS = {
    'DEFAULT_RATE_LIMIT': '100/hour',
    'LOGIN_RATE_LIMIT': '5/min',
    'REGISTRATION_RATE_LIMIT': '3/min',
    'PASSWORD_RESET_RATE_LIMIT': '3/hour',
    'API_RATE_LIMIT': '1000/hour',
}


# Security checklist for production
PRODUCTION_SECURITY_CHECKLIST = [
    "Set DEBUG = False",
    "Use strong SECRET_KEY",
    "Configure ALLOWED_HOSTS properly",
    "Use HTTPS (SECURE_SSL_REDIRECT = True)",
    "Set secure cookie flags",
    "Configure HSTS headers",
    "Use environment variables for secrets",
    "Enable database SSL",
    "Configure proper logging",
    "Set up monitoring",
    "Regular security updates",
    "Backup strategy",
    "Error tracking (Sentry)",
    "Rate limiting",
    "CSRF protection",
    "XSS protection",
    "Content type validation",
]
