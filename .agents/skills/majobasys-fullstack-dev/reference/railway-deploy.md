# Deployment en Railway - MajobaSYS

## Guía Paso a Paso

### 1. Preparar el Proyecto

#### Crear requirements.txt

```txt
Django==5.2
python-decouple==3.8
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
django-redis==5.4.0
redis==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
drf-spectacular==0.27.0
```

#### Crear runtime.txt

```txt
python-3.11.7
```

#### Crear Procfile

```
web: gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 3
release: python majobacore/manage.py migrate
```

#### Crear railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. Configurar Settings de Producción

Actualizar `majobacore/settings/production.py`:

```python
import dj_database_url
from .base import *

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS para React Native (futuro)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())

# Static files con WhiteNoise
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Crear Proyecto en Railway

1. Ir a [railway.app](https://railway.app)
2. Crear cuenta o login
3. Click "New Project"
4. Seleccionar "Deploy from GitHub repo"
5. Autorizar Railway en GitHub
6. Seleccionar repositorio MajobaSYS-1

### 4. Configurar Variables de Entorno

En Railway Dashboard → Variables:

```env
# Django
SECRET_KEY=<generar-con-manage.py-generate_secret_key>
DEBUG=False
DJANGO_SETTINGS_MODULE=majobacore.settings.production
ALLOWED_HOSTS=*.up.railway.app,tudominio.com

# Database (Railway lo provee automáticamente)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (agregar Railway Redis addon)
REDIS_URL=${{Redis.REDIS_URL}}

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@majobasys.com

# Security
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://*.up.railway.app
CORS_ALLOWED_ORIGINS=https://tudominio.com

# Otros
LANGUAGE_CODE=es-es
TIME_ZONE=America/Mexico_City
```

### 5. Agregar PostgreSQL

1. En Railway Dashboard
2. Click "+ New"
3. Seleccionar "Database" → "PostgreSQL"
4. Railway automáticamente configura DATABASE_URL

### 6. Agregar Redis (Opcional pero Recomendado)

1. En Railway Dashboard
2. Click "+ New"
3. Seleccionar "Database" → "Redis"
4. Railway automáticamente configura REDIS_URL

### 7. Deploy

```bash
# Railway detecta cambios automáticamente en git push
git add .
git commit -m "Configure for Railway deployment"
git push origin main

# O deploy manual con Railway CLI
npm install -g @railway/cli
railway login
railway link
railway up
```

### 8. Comandos Post-Deploy

```bash
# Ejecutar migraciones
railway run python majobacore/manage.py migrate

# Crear superusuario
railway run python majobacore/manage.py createsuperuser

# Collectstatic (WhiteNoise lo hace automáticamente)
railway run python majobacore/manage.py collectstatic --noinput

# Ver logs
railway logs
```

### 9. Configurar Dominio Custom (Opcional)

1. En Railway Dashboard → Settings → Domains
2. Click "Generate Domain" (obtener *.up.railway.app gratis)
3. O agregar dominio custom:
   - Click "Custom Domain"
   - Agregar tu dominio (ej: api.majobasys.com)
   - Configurar DNS según instrucciones de Railway

### 10. Monitoreo y Logs

```bash
# Ver logs en tiempo real
railway logs --follow

# Ver métricas
railway status

# Ver variables
railway variables

# Abrir shell
railway run python majobacore/manage.py shell

# Abrir psql
railway run python majobacore/manage.py dbshell
```

## Troubleshooting Común

### Error: ModuleNotFoundError

**Causa**: Falta librería en requirements.txt  
**Solución**: Agregar librería y hacer redeploy

### Error: Static files not found

**Causa**: WhiteNoise mal configurado  
**Solución**: Verificar STATIC_ROOT y STATICFILES_STORAGE en settings

### Error: Database connection failed

**Causa**: DATABASE_URL incorrecta  
**Solución**: Verificar variable ${{Postgres.DATABASE_URL}} en Railway

### Error: DisallowedHost

**Causa**: Dominio no en ALLOWED_HOSTS  
**Solución**: Agregar dominio a ALLOWED_HOSTS en Railway variables

### Error: CSRF verification failed

**Causa**: CSRF_TRUSTED_ORIGINS mal configurado  
**Solución**: Agregar https://tudominio.com a CSRF_TRUSTED_ORIGINS

## Checklist Pre-Deploy

- [ ] requirements.txt actualizado
- [ ] Procfile creado
- [ ] railway.json configurado
- [ ] Settings de producción listos
- [ ] SECRET_KEY generada y segura
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] Database migrada
- [ ] Static files testeados
- [ ] Logs revisados
- [ ] Health check funcionando

## Costos Estimados

- **Hobby Plan** (gratis): 500 horas/mes, 1GB RAM, 1GB storage
- **Pro Plan** ($20/mes): Uso ilimitado, 8GB RAM, 100GB storage
- **PostgreSQL**: $5/mes (512MB RAM) a $50/mes (8GB RAM)
- **Redis**: $2/mes (50MB) a $20/mes (1GB)

**Estimado inicial**: ~$0-10/mes para desarrollo/staging

## Links Útiles

- [Railway Docs](https://docs.railway.app/)
- [Railway Django Template](https://railway.app/template/GB6Eki)
- [Railway CLI](https://docs.railway.app/develop/cli)
