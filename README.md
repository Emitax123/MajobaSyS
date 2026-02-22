# MajobaSyS

Sistema de gestión empresarial construido con Django 5.2+ y desplegado en Railway.

## 🚀 Despliegue en Railway

Este proyecto está configurado para desplegarse automáticamente en Railway usando Nixpacks.

### Archivos de Configuración

- **`nixpacks.toml`**: Configuración de build para Nixpacks
- **`railway.json`**: Configuración de Railway (restart policy, healthcheck)
- **`Procfile`**: Comandos de release (migraciones) y web (Gunicorn)
- **`runtime.txt`**: Versión de Python (3.11)

### Variables de Entorno Requeridas

```env
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=tu-app.up.railway.app
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
REDIS_URL=redis://...
EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

## 📦 Estructura del Proyecto

```
MajobaSyS/
├── manage.py                  # Django management script
├── Procfile                   # Railway commands
├── railway.json               # Railway config
├── nixpacks.toml              # Nixpacks build config
├── runtime.txt                # Python version
├── requirements/              # Python dependencies
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── majobacore/                # Django project package
│   ├── settings/
│   ├── management/
│   └── utils/
├── users/                     # Authentication app
├── manager/                   # Management app
├── static/                    # Static files
└── templates/                 # Django templates
```

## 🛠️ Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements/development.txt

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

## 📚 Documentación

- **[AGENTS.md](./AGENTS.md)**: Documentación para agentes IA
- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Guía de despliegue detallada
- **[PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)**: Checklist de producción
- **[README_DJANGO.md](./README_DJANGO.md)**: README original del proyecto Django

## 🔐 Seguridad

- Django 5.2+ con settings modulares (development/production/testing)
- PostgreSQL en producción, SQLite en desarrollo
- Redis para cache y sesiones
- HTTPS redirect, HSTS, secure cookies
- WhiteNoise para archivos estáticos
- Gunicorn como WSGI server

## 📝 Licencia

Privado - Uso interno
