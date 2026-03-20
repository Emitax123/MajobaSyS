"""
Utilidades HTTP para el proyecto MajobaSyS.
"""


def get_client_ip(request):
    """
    Retorna la IP del cliente a partir del request de Django.

    Extrae el primer valor de X-Forwarded-For (el cliente real) y cae
    a REMOTE_ADDR cuando el header no está presente. Devuelve
    'desconocida' si el request es None.

    Args:
        request: HttpRequest de Django, o None.

    Returns:
        str: Dirección IP del cliente.
    """
    if request is None:
        return 'desconocida'

    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()

    return request.META.get('REMOTE_ADDR', 'desconocida')
