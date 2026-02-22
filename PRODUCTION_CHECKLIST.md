# ✅ Checklist de Preparación para Producción - MajobaSyS

**Proyecto**: MajobaSyS (MajobaCore)  
**Plataforma**: Railway  
**Fecha**: Febrero 2026

---

## 📦 Archivos Creados/Modificados

### ✅ Archivos Nuevos
- [x] `.env.example` - Template de variables de entorno
- [x] `DEPLOYMENT.md` - Guía completa de deployment
- [x] `PRODUCTION_CHECKLIST.md` - Este archivo
- [x] `majobacore/management/commands/check_production_settings.py` - Comando de validación
- [x] Health check endpoints en `majobacore/views.py`

### ✅ Archivos Modificados
- [x] `majobacore/settings/base.py` - Optimizado para producción
- [x] `majobacore/settings/production.py` - Configuración completa Railway
- [x] `majobacore/utils/security.py` - Middleware de seguridad mejorado
- [x] `majobacore/urls.py` - Agregados health check endpoints
- [x] `requirements/base.txt` - Agregado python-json-logger
- [x] `requirements/production.txt` - Agregado django-cors-headers

---

## 🚀 Pasos Antes de Deployar

### 1. Verificar Localmente

```bash
cd majobacore

# Instalar dependencias
pip install -r requirements/production.txt

# Generar SECRET_KEY nuevo
python manage.py generate_secret_key
# ⚠️ GUARDAR ESTE KEY en un lugar seguro

# Validar configuración (simulando producción)
python manage.py check_production_settings

# Check de Django
python manage.py check --deploy
```

### 2. Crear .env para Desarrollo (Opcional)

```bash
# Copiar template
cp .env.example .env

# Editar .env con tus valores de desarrollo
nano .env
```

**⚠️ NUNCA commitear .env a Git** (ya está en .gitignore)

### 3. Commit y Push

```bash
git add .
git commit -m "feat: configuración de producción completa para Railway"
git push origin main
```

---

## 🚂 Configuración de Railway

### 1. Servicios a Crear
- [ ] Django Application (desde GitHub)
- [ ] PostgreSQL Database
- [ ] Redis Database

### 2. Variables de Entorno Obligatorias

```bash
# Core
SECRET_KEY=<generar-nuevo>
DEBUG=False
DJANGO_SETTINGS_MODULE=majobacore.settings.production
ALLOWED_HOSTS=tu-app.railway.app

# Database (usar referencias de Railway)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}

# Cache
REDIS_URL=${{Redis.REDIS_URL}}

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://tu-app.railway.app
```

### 3. Variables Opcionales pero Recomendadas

```bash
# Email (cambiar con tus valores reales)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@tudominio.com
SERVER_EMAIL=admin@tudominio.com
ADMIN_EMAIL=admin@tudominio.com

# Monitoring
SENTRY_DSN=<opcional-para-errores>

# AWS S3 (si usas)
USE_S3=False
```

Ver `.env.example` para la lista completa con explicaciones.

---

## ✅ Post-Deployment Checklist

### Verificaciones Inmediatas

```bash
# 1. Health Check
curl https://tu-app.railway.app/health/

# 2. Liveness
curl https://tu-app.railway.app/health/live/

# 3. Readiness
curl https://tu-app.railway.app/health/ready/

# 4. Página principal
curl https://tu-app.railway.app/
```

### Crear Superusuario

```bash
# Opción 1: Railway CLI
railway run python manage.py createsuperuser

# Opción 2: Railway Dashboard
# Settings > Service > One-off Commands
python manage.py createsuperuser
```

### Verificar Funcionalidad

- [ ] `/` - Página principal carga
- [ ] `/admin/` - Admin accesible
- [ ] `/health/` - Health check OK
- [ ] Login funciona
- [ ] Archivos estáticos cargan (CSS/JS)
- [ ] Formularios funcionan (CSRF)
- [ ] Sin errores en logs

---

## 🔐 Configuraciones de Seguridad Implementadas

### HTTP Security Headers
✅ Content-Security-Policy (CSP)  
✅ X-Content-Type-Options: nosniff  
✅ X-Frame-Options: DENY  
✅ X-XSS-Protection: 1; mode=block  
✅ Referrer-Policy: strict-origin-when-cross-origin  
✅ Permissions-Policy (cámara, micrófono, etc. bloqueados)  
✅ Cross-Origin-Embedder-Policy  
✅ Cross-Origin-Opener-Policy  
✅ Cross-Origin-Resource-Policy  

### SSL/HTTPS
✅ SECURE_SSL_REDIRECT = True  
✅ SECURE_PROXY_SSL_HEADER configurado  
✅ HSTS habilitado (1 año)  
✅ HSTS include subdomains  
✅ HSTS preload ready  

### Cookies
✅ SESSION_COOKIE_SECURE = True  
✅ CSRF_COOKIE_SECURE = True  
✅ SESSION_COOKIE_HTTPONLY = True  
✅ CSRF_COOKIE_HTTPONLY = True  
✅ SameSite = Lax  

### Database
✅ PostgreSQL con SSL requerido  
✅ Connection pooling (CONN_MAX_AGE = 600)  
✅ Atomic requests por defecto  
✅ Statement timeout (30s)  

### Cache/Sessions
✅ Redis para cache  
✅ Redis para sesiones  
✅ Connection pooling  
✅ Compresión habilitada  
✅ Fallback graceful si Redis falla  

### Logging
✅ JSON structured logs  
✅ Logs a stdout para Railway  
✅ Rotación de archivos (10MB, 5 backups)  
✅ Diferentes niveles por ambiente  
✅ Email admins en errores (opcional)  

### Validación de Inputs
✅ Passwords mínimo 12 caracteres  
✅ Validadores de Django habilitados  
✅ CSRF protection en todos los forms  
✅ Límites de upload (5MB)  

---

## 📊 Endpoints de Monitoreo

### Health Checks

| Endpoint | Propósito | Respuesta |
|----------|-----------|-----------|
| `/health/` | Health check completo (DB + Cache) | JSON con status |
| `/health/live/` | Liveness probe (app viva) | `OK` (200) |
| `/health/ready/` | Readiness probe (lista para tráfico) | `Ready` (200) |

Railway usa `/health/` automáticamente para verificar el estado.

---

## 🛠️ Comandos Útiles

### Validación de Producción

```bash
# Validar configuración de seguridad
railway run python manage.py check_production_settings

# Check de Django con deployment checks
railway run python manage.py check --deploy

# Generar nuevo SECRET_KEY
railway run python manage.py generate_secret_key
```

### Gestión de Base de Datos

```bash
# Ver migraciones
railway run python manage.py showmigrations

# Aplicar migraciones
railway run python manage.py migrate

# Crear superusuario
railway run python manage.py createsuperuser

# Django shell
railway run python manage.py shell
```

### Railway CLI

```bash
# Instalar
npm i -g @railway/cli

# Login
railway login

# Linkar proyecto
railway link

# Ver variables
railway variables

# Ver logs
railway logs

# Ejecutar comando
railway run <comando>
```

---

## 🐛 Troubleshooting Común

### Error: `SECRET_KEY must be set`
**Solución**: Generar y configurar SECRET_KEY en Railway:
```bash
python manage.py generate_secret_key
# Copiar resultado a Railway > Settings > Variables
```

### Error: `ALLOWED_HOSTS validation error`
**Solución**: Agregar dominio de Railway:
```bash
ALLOWED_HOSTS=tu-app.railway.app
```

### Error: `could not connect to server`
**Solución**: Verificar variables de PostgreSQL:
```bash
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
# etc. (usar referencias, no valores hardcodeados)
```

### Error: Archivos estáticos 404
**Solución**: Verificar que collectstatic se ejecutó:
```bash
railway run python manage.py collectstatic --noinput
```

### Error: CSRF verification failed
**Solución**: Agregar dominio a CSRF_TRUSTED_ORIGINS:
```bash
CSRF_TRUSTED_ORIGINS=https://tu-app.railway.app
```

Ver `DEPLOYMENT.md` para troubleshooting completo.

---

## 📚 Documentación Adicional

- **DEPLOYMENT.md** - Guía paso a paso detallada
- **.env.example** - Template de variables con explicaciones
- **AGENTS.md** - Información del proyecto para agentes IA
- **Railway Docs** - https://docs.railway.app/

---

## 🎯 Checklist Final Antes de Producción

### Pre-Deployment
- [ ] Código en GitHub actualizado
- [ ] SECRET_KEY generado (nuevo, seguro)
- [ ] `.env.example` documentado
- [ ] `check_production_settings` pasa sin errores
- [ ] `check --deploy` pasa sin warnings críticos
- [ ] Tests pasando (si existen)

### Railway Setup
- [ ] Proyecto creado en Railway
- [ ] PostgreSQL agregado
- [ ] Redis agregado
- [ ] Variables de entorno configuradas
- [ ] Referencias de servicios correctas (`${{Postgres.PGDATABASE}}`)

### Post-Deployment
- [ ] Build exitoso
- [ ] Migraciones aplicadas
- [ ] Gunicorn corriendo
- [ ] Health checks OK
- [ ] Superusuario creado
- [ ] Admin accesible
- [ ] Login funciona
- [ ] Logs sin errores críticos

### Seguridad
- [ ] DEBUG=False
- [ ] SECRET_KEY único
- [ ] ALLOWED_HOSTS configurado
- [ ] HTTPS habilitado (automático Railway)
- [ ] Cookies seguras
- [ ] CSRF configurado
- [ ] Security headers activos

### Opcional
- [ ] Dominio personalizado configurado
- [ ] Sentry configurado
- [ ] Email SMTP configurado
- [ ] Backups configurados
- [ ] Monitoring setup

---

## ✅ Estado Actual

**Configuración completada**: ✅ 100%

Todos los archivos de configuración han sido creados y optimizados siguiendo las mejores prácticas de Django y seguridad web.

**Próximo paso**: Seguir la guía en `DEPLOYMENT.md` para deployar en Railway.

---

**¿Preguntas?** Consulta `DEPLOYMENT.md` o revisa los comentarios en:
- `majobacore/settings/production.py`
- `majobacore/utils/security.py`
- `.env.example`

**¡Listo para producción!** 🚀
