"""
Views for MajobaCore main pages and utilities.
"""

import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.core.mail import send_mail
from smtplib import SMTPException

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
    """
    Formulario de solicitud de presupuesto.

    GET  → Renderiza el formulario vacío.
    POST → Valida los campos, envía un mail a la cuenta de la empresa
           (EMAIL_HOST_USER) con los datos del solicitante y devuelve
           feedback de éxito o error al usuario.
    """
    if request.method != 'POST':
        return render(request, 'budget_form.html')

    # Leer y limpiar campos del formulario
    name            = request.POST.get('name', '').strip()
    phone           = request.POST.get('phone', '').strip()
    email           = request.POST.get('email', '').strip()
    project_details = request.POST.get('project_details', '').strip()

    # Validación básica — los campos son required en el template,
    # pero validamos también en el servidor por seguridad.
    if not all([name, phone, email, project_details]):
        return render(request, 'budget_form.html', {
            'error': 'Por favor completá todos los campos del formulario.',
            'form_data': {
                'name': name,
                'phone': phone,
                'email': email,
                'project_details': project_details,
            },
        })

    subject = f'Nueva solicitud de presupuesto — {name}'

    message = (
        f'Se recibió una nueva solicitud de presupuesto a través del sitio web.\n\n'
        f'--- DATOS DEL SOLICITANTE ---\n'
        f'Nombre:   {name}\n'
        f'Teléfono: {phone}\n'
        f'Email:    {email}\n\n'
        f'--- DETALLES DEL PROYECTO ---\n'
        f'{project_details}\n'
    )

    company_email = settings.EMAIL_HOST_USER

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[company_email],
            fail_silently=False,
        )
        logger.info(
            f'Presupuesto enviado correctamente | solicitante: {email} | nombre: {name}'
        )
        return render(request, 'budget_form.html', {'success': True})

    except SMTPException as e:
        logger.error(f'Error SMTP al enviar presupuesto de {email}: {e}')
        return render(request, 'budget_form.html', {
            'error': 'Hubo un problema al enviar tu solicitud. Por favor intentá más tarde o contactanos directamente.',
            'form_data': {
                'name': name,
                'phone': phone,
                'email': email,
                'project_details': project_details,
            },
        })
    except Exception as e:
        logger.error(f'Error inesperado al enviar presupuesto de {email}: {e}')
        return render(request, 'budget_form.html', {
            'error': 'Ocurrió un error inesperado. Por favor intentá más tarde.',
            'form_data': {
                'name': name,
                'phone': phone,
                'email': email,
                'project_details': project_details,
            },
        })


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


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def liveness_check(request):
    """
    Liveness probe para Railway.
    Verifica que la aplicación está ejecutándose.
    
    Este endpoint es ultra-ligero y NO verifica dependencias externas.
    Railway lo usa para determinar si el contenedor está vivo.
    
    Returns:
        HttpResponse: 200 OK si la app está viva
    """
    # Respuesta simple y rápida - sin verificar DB ni cache
    return HttpResponse("OK", status=200, content_type="text/plain")


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
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
        return HttpResponse("Ready", status=200, content_type="text/plain")
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return HttpResponse("Not Ready", status=503, content_type="text/plain")