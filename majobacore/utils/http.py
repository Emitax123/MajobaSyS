"""
Utilidades HTTP para el proyecto MajobaSyS.
"""
import ipaddress
import logging

from django.conf import settings

logger = logging.getLogger('majobacore')


def get_client_ip(request):
    """
    Retorna la IP del cliente a partir del request de Django.

    Si TRUSTED_PROXY_ENABLED está activo en settings, extrae el primer valor
    de X-Forwarded-For (el cliente real). De lo contrario, usa solo REMOTE_ADDR.
    En ambos casos valida que el valor sea una IP bien formada; si no lo es,
    cae a 'desconocida' para evitar log forging.

    Args:
        request: HttpRequest de Django, o None.

    Returns:
        str: Dirección IP del cliente validada, o 'desconocida'.
    """
    if request is None:
        return 'desconocida'

    trusted_proxy = getattr(settings, 'TRUSTED_PROXY_ENABLED', False)

    if trusted_proxy:
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            raw_ip = forwarded_for.split(',')[0].strip()
            return _validate_ip(raw_ip)

    return _validate_ip(request.META.get('REMOTE_ADDR', ''))


def _validate_ip(value):
    """
    Valida que el valor sea una dirección IP bien formada.

    Args:
        value (str): Valor a validar.

    Returns:
        str: La IP si es válida, 'desconocida' en caso contrario.
    """
    if not value:
        return 'desconocida'
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError:
        logger.warning("IP inválida o malformada recibida en request: %r", value)
        return 'desconocida'
