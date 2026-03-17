"""
Throttling personalizado para la API REST de MajobaSyS.
"""
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Rate limit para el endpoint de login."""
    scope = 'login'
