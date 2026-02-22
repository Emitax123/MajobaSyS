"""
Views for MajobaCore main pages and utilities.
"""

import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger('majobacore')


# ============================================================================
# PÁGINAS PRINCIPALES
# ============================================================================

def index(request):
    """Landing page del sistema."""
    return render(request, 'index.html')


def majoba_view(request):
    """Página de Majoba."""
    return render(request, 'majoba_template.html')


def hormicons_view(request):
    """Página de Hormicons."""
    return render(request, 'hormicons_template.html')


def constructora_view(request):
    """Página de Constructora."""
    return render(request, 'constructora_template.html')


def budget_view(request):
    """Formulario de presupuesto."""
    return render(request, 'budget_form.html')


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Health check endpoint para Railway.
    
    Verifica:
    - Que la aplicación está respondiendo
    - Conexión a base de datos
    - Conexión a Redis (cache)
    
    Returns:
        JsonResponse: Status de salud de la aplicación
    """
    health_status = {
        'status': 'healthy',
        'environment': settings.DEBUG and 'development' or 'production',
        'checks': {}
    }
    
    # Check base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'error: {str(e)}'
        logger.error(f"Health check - Database error: {e}")
    
    # Check cache (Redis)
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'degraded'
    except Exception as e:
        health_status['status'] = 'degraded'  # No crítico
        health_status['checks']['cache'] = f'error: {str(e)}'
        logger.warning(f"Health check - Cache error: {e}")
    
    # Status code según resultado
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness probe para Railway.
    Verifica que la aplicación está ejecutándose.
    
    Returns:
        HttpResponse: 200 OK si la app está viva
    """
    return HttpResponse("OK", status=200)


@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness probe para Railway.
    Verifica que la aplicación está lista para recibir tráfico.
    
    Returns:
        HttpResponse: 200 OK si la app está lista
    """
    try:
        # Verificar conexión a BD
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return HttpResponse("Ready", status=200)
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return HttpResponse("Not Ready", status=503)