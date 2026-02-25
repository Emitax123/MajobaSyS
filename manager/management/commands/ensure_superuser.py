"""
Comando de gestión para crear el superusuario automáticamente en Railway.

Lee las credenciales desde variables de entorno y crea el superusuario
solo si no existe. Es idempotente: se puede ejecutar múltiples veces
sin efectos secundarios.

Variables de entorno requeridas:
    SUPERUSER_USERNAME  — Nombre de usuario del superusuario
    SUPERUSER_PASSWORD  — Contraseña del superusuario

Variables de entorno opcionales:
    SUPERUSER_EMAIL      — Email del superusuario (default: vacío)
    SUPERUSER_FIRST_NAME — Nombre (default: 'Admin')
    SUPERUSER_LAST_NAME  — Apellido (default: 'Admin')
    SUPERUSER_PHONE      — Teléfono (default: '0000000000')

Uso:
    python manage.py ensure_superuser
    python manage.py ensure_superuser --settings=majobacore.settings.production
"""

import logging
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

logger = logging.getLogger('majobacore')


class Command(BaseCommand):
    help = (
        'Crea el superusuario desde variables de entorno si no existe. '
        'Idempotente: no hace nada si el usuario ya existe.'
    )

    def handle(self, *args, **options):
        User = get_user_model()

        # ------------------------------------------------------------------ #
        # 1. Leer variables de entorno
        # ------------------------------------------------------------------ #
        username = os.environ.get('SUPERUSER_USERNAME', '').strip()
        password = os.environ.get('SUPERUSER_PASSWORD', '').strip()

        # Opcionales
        email = os.environ.get('SUPERUSER_EMAIL', '').strip()
        first_name = os.environ.get('SUPERUSER_FIRST_NAME', 'Admin').strip()
        last_name = os.environ.get('SUPERUSER_LAST_NAME', 'Admin').strip()
        phone = os.environ.get('SUPERUSER_PHONE', '0000000000').strip()

        # ------------------------------------------------------------------ #
        # 2. Validar variables obligatorias
        # ------------------------------------------------------------------ #
        missing = []
        if not username:
            missing.append('SUPERUSER_USERNAME')
        if not password:
            missing.append('SUPERUSER_PASSWORD')

        if missing:
            raise CommandError(
                f"Faltan variables de entorno obligatorias: {', '.join(missing)}\n"
                "Configúralas en Railway Dashboard → Variables antes de desplegar."
            )

        # ------------------------------------------------------------------ #
        # 3. Validaciones básicas de seguridad
        # ------------------------------------------------------------------ #
        if len(password) < 8:
            raise CommandError(
                "SUPERUSER_PASSWORD debe tener al menos 8 caracteres."
            )

        # ------------------------------------------------------------------ #
        # 4. Verificar si ya existe
        # ------------------------------------------------------------------ #
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"[ensure_superuser] El usuario '{username}' ya existe. "
                    "No se realizaron cambios."
                )
            )
            logger.info(f"ensure_superuser: usuario '{username}' ya existe, omitiendo.")
            return

        # ------------------------------------------------------------------ #
        # 5. Crear superusuario
        # ------------------------------------------------------------------ #
        try:
            with transaction.atomic():
                user = User.objects.create_superuser(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )

                # CustomUser tiene campo phone (requerido en el modelo)
                if hasattr(user, 'phone'):
                    user.phone = phone
                    user.save(update_fields=['phone'])

            self.stdout.write(
                self.style.SUCCESS(
                    f"[ensure_superuser] Superusuario '{username}' creado correctamente."
                )
            )
            logger.info(f"ensure_superuser: superusuario '{username}' creado exitosamente.")

        except Exception as exc:
            logger.error(f"ensure_superuser: error al crear superusuario — {exc}")
            raise CommandError(
                f"Error al crear el superusuario '{username}': {exc}"
            ) from exc
