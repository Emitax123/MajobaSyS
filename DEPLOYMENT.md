# 🚀 Guía de Deployment - MajobaSyS en Railway

Esta guía te ayudará a desplegar MajobaSyS en Railway con todas las configuraciones de producción optimizadas.

---

## 📋 Tabla de Contenidos

1. [Pre-requisitos](#pre-requisitos)
2. [Preparación Local](#preparación-local)
3. [Configuración de Railway](#configuración-de-railway)
4. [Variables de Entorno](#variables-de-entorno)
5. [Despliegue](#despliegue)
6. [Verificación Post-Deployment](#verificación-post-deployment)
7. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Pre-requisitos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta en [Railway](https://railway.app/)
- ✅ Cuenta en [GitHub](https://github.com/) (tu repositorio ya debe estar conectado)
- ✅ Python 3.11+ instalado localmente
- ✅ Git configurado y repositorio con los últimos cambios
- ✅ (Opcional) Cuenta en [Sentry](https://sentry.io/) para monitoreo de errores

---

## 🔧 Preparación Local

### 1. Validar Configuración Local

Antes de desplegar, verifica que todo funciona localmente:

```bash
cd majobacore

# Instalar dependencias de producción
pip install -r requirements/production.txt

# Verificar configuración de producción (sin aplicarla)
python manage.py check_production_settings

# Verificar que no hay problemas
python manage.py check --deploy --settings=majobacore.settings.production
```

### 2. Generar SECRET_KEY Nuevo

```bash
python manage.py generate_secret_key
```

**⚠️ IMPORTANTE**: Guarda este SECRET_KEY en un lugar seguro, lo necesitarás para Railway.

### 3. Verificar Archivos de Configuración

Asegúrate de que estos archivos existen y están actualizados:

- ✅ `requirements.txt` - Indicador para Nixpacks (apunta a production.txt)
- ✅ `runtime.txt` - Versión de Python
- ✅ `Procfile` - Comando web (migrate + gunicorn)
- ✅ `railway.toml` - Builder, buildCommand, healthcheck
- ✅ `requirements/production.txt` - Dependencias de producción
- ✅ `majobacore/settings/production.py` - Settings de producción
- ✅ `.env.example` - Template de variables de entorno

### 4. Commit y Push

```bash
git add .
git commit -m "chore: preparar configuración de producción para Railway"
git push origin main
```

---

## 🚂 Configuración de Railway

### 1. Crear Nuevo Proyecto

1. Ve a [Railway Dashboard](https://railway.app/dashboard)
2. Click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Selecciona tu repositorio **MajobaSyS**
5. Railway detectará automáticamente que es un proyecto Django

### 2. Agregar PostgreSQL

1. En tu proyecto, click en **"+ New"**
2. Selecciona **"Database"**
3. Selecciona **"Add PostgreSQL"**
4. Railway creará la base de datos y generará las variables automáticamente

### 3. Agregar Redis

1. En tu proyecto, click en **"+ New"**
2. Selecciona **"Database"**
3. Selecciona **"Add Redis"**
4. Railway creará Redis y generará las variables automáticamente

---

## 🔐 Variables de Entorno

### Variables Automáticas (Railway las proporciona)

Railway genera automáticamente estas variables cuando agregas PostgreSQL y Redis:

- `DATABASE_URL` (pero usamos las individuales)
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- `REDIS_URL`
- `PORT`
- `RAILWAY_ENVIRONMENT`
- `RAILWAY_STATIC_URL`

### Variables que DEBES Configurar Manualmente

Ve a **Settings > Variables** en Railway y agrega:

#### **CRÍTICAS** (Obligatorias)

```bash
# Django Core
SECRET_KEY=<tu-secret-key-generado>
DEBUG=False
DJANGO_SETTINGS_MODULE=majobacore.settings.production

# Hosts permitidos (separados por coma, SIN espacios)
ALLOWED_HOSTS=tu-app.railway.app,tudominio.com

# Base de datos (usar las variables de Railway)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}

# Cache/Sessions
REDIS_URL=${{Redis.REDIS_URL}}
```

#### **IMPORTANTES** (Recomendadas)

```bash
# Seguridad
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CSRF Trusted Origins (tu dominio Railway)
CSRF_TRUSTED_ORIGINS=https://tu-app.railway.app,https://tudominio.com

# Email (configurar con tu proveedor SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@tudominio.com
SERVER_EMAIL=admin@tudominio.com
ADMIN_EMAIL=admin@tudominio.com
```

#### **OPCIONALES** (Mejoran la experiencia)

```bash
# Sentry para monitoreo de errores
SENTRY_DSN=<tu-sentry-dsn>

# AWS S3 para archivos media (si usas)
USE_S3=True
AWS_ACCESS_KEY_ID=<tu-aws-access-key>
AWS_SECRET_ACCESS_KEY=<tu-aws-secret-key>
AWS_STORAGE_BUCKET_NAME=<tu-bucket>
AWS_S3_REGION_NAME=us-east-1

# Admin URL personalizado (security by obscurity)
ADMIN_URL=secret-admin-panel-xyz/
```

### 📝 Template de Variables para Railway

Puedes copiar y pegar este template en Railway (ajustando los valores):

```bash
SECRET_KEY=<generar-con-generate_secret_key>
DEBUG=False
DJANGO_SETTINGS_MODULE=majobacore.settings.production
ALLOWED_HOSTS=tu-app.railway.app
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
REDIS_URL=${{Redis.REDIS_URL}}
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://tu-app.railway.app
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@tudominio.com
SERVER_EMAIL=admin@tudominio.com
ADMIN_EMAIL=admin@tudominio.com
```

---

## 🚀 Despliegue

### Proceso de Deployment

Railway + Nixpacks ejecuta estos pasos automáticamente:

1. **Detección**: Nixpacks detecta Python por `requirements.txt` en la raíz y versión por `runtime.txt`
2. **Install** (automático): `pip install -r requirements.txt` (apunta a `requirements/production.txt`)
3. **Build** (configurado en `railway.toml`):
   ```bash
   python manage.py collectstatic --noinput --settings=majobacore.settings.production
   ```
   > `collectstatic` activa `IS_BUILD_PHASE` en `production.py`, que usa DB dummy (SQLite :memory:) y DummyCache para no necesitar PostgreSQL ni Redis durante el build.
4. **Start** (definido en `Procfile`):
   ```bash
   python manage.py migrate --settings=majobacore.settings.production --noinput && gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
   ```
   > Las migraciones se ejecutan en cada start (antes de gunicorn). Es idempotente.

**Archivos clave de configuración:**
| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Indicador para Nixpacks (`-r requirements/production.txt`) |
| `runtime.txt` | Versión de Python (`python-3.11`) |
| `railway.toml` | Builder, buildCommand, healthcheck, restart policy |
| `Procfile` | Comando `web:` (migrate + gunicorn) |

### Trigger del Deployment

El deployment se activa automáticamente cuando:
- Haces push a la rama `main` (o la rama configurada)
- Cambias variables de entorno en Railway
- Haces click en **"Deploy"** manualmente

### Monitorear el Deployment

1. Ve a la pestaña **"Deployments"** en Railway
2. Click en el deployment activo
3. Observa los logs en tiempo real
4. Verifica que:
   - ✅ Build completó exitosamente
   - ✅ Migraciones se aplicaron
   - ✅ Servidor Gunicorn está corriendo

---

## ✅ Verificación Post-Deployment

### 1. Health Check

Verifica que la aplicación está funcionando:

```bash
# Health check completo
curl https://tu-app.railway.app/health/

# Liveness check
curl https://tu-app.railway.app/health/live/

# Readiness check
curl https://tu-app.railway.app/health/ready/
```

**Respuesta esperada** (health check):
```json
{
  "status": "healthy",
  "environment": "production",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

### 2. Verificar Página Principal

```bash
curl https://tu-app.railway.app/
```

Debe responder con tu página de inicio (código 200).

### 3. Verificar Admin

```bash
# Visitar admin (reemplaza con tu URL)
https://tu-app.railway.app/admin/
```

### 4. Crear Superusuario

Necesitas crear un superusuario para acceder al admin:

**Opción 1: Usando Railway CLI**

```bash
railway run python manage.py createsuperuser
```

**Opción 2: Desde el Dashboard de Railway**

1. Ve a tu servicio Django
2. Click en **"Settings"** > **"Service"**
3. Click en **"One-off Commands"**
4. Ejecuta:
   ```bash
   python manage.py createsuperuser --username admin --email admin@tudominio.com
   ```

### 5. Verificar Logs

En Railway Dashboard:
1. Ve a tu servicio Django
2. Click en la pestaña **"Logs"**
3. Verifica que no hay errores críticos
4. Busca el mensaje: `Production settings loaded successfully`

### 6. Probar Funcionalidad

- [ ] Login funciona
- [ ] Páginas cargan correctamente
- [ ] Archivos estáticos se sirven (CSS, JS, imágenes)
- [ ] Formularios funcionan (CSRF)
- [ ] Base de datos responde
- [ ] Cache funciona

---

## 📊 Monitoreo y Mantenimiento

### Logs

**Ver logs en tiempo real:**

```bash
railway logs
```

**Ver logs específicos:**
- **Deployment logs**: Pestaña "Deployments" > Click en deployment
- **Application logs**: Pestaña "Logs" del servicio
- **Database logs**: Pestaña "Logs" de PostgreSQL

### Métricas

Railway proporciona métricas automáticas:
- **CPU Usage**
- **Memory Usage**
- **Network Traffic**
- **Request Count**
- **Response Times**

Accede a: **Metrics** tab en tu servicio.

### Health Checks Configurados

Railway verifica automáticamente:
- **Path**: `/health/live/` (configurado en `railway.toml`)
- **Timeout**: 100 segundos
- **Restart policy**: `ON_FAILURE`, max 10 retries

**Importante:** Railway hace health checks por **HTTP interno** (no HTTPS). Por eso `SECURE_REDIRECT_EXEMPT = [r'^health/']` es obligatorio en `production.py` — sin esto, Django responde 301 redirect y Railway lo interpreta como fallo.

### Backups de Base de Datos

**Railway no hace backups automáticos** en el plan gratuito.

**Backup manual:**

```bash
# Usando Railway CLI
railway run pg_dump -U postgres -d railway > backup.sql

# Restaurar
railway run psql -U postgres -d railway < backup.sql
```

**Recomendación**: Configura backups automáticos con un cron job o servicio externo.

### Monitoreo con Sentry (Recomendado)

Si configuraste Sentry:

1. Ve a [sentry.io](https://sentry.io/)
2. Crea un proyecto Django
3. Copia el DSN
4. Agrégalo a Railway como `SENTRY_DSN`

Sentry capturará automáticamente:
- ❌ Errores 500
- ⚠️ Excepciones no manejadas
- 🐛 Stack traces completos
- 📊 Performance metrics

---

## 🔧 Troubleshooting

### Problema: Nixpacks No Detecta Python

**Síntomas**: `Nixpacks was unable to generate a build plan for this app`

**Causa**: No existe `requirements.txt` en la raíz del proyecto. Nixpacks no reconoce `requirements/` (carpeta) como indicador de Python.

**Solución**: Crear `requirements.txt` en la raíz:
```
-r requirements/production.txt
```

### Problema: `pip: command not found` durante build

**Síntomas**: `RUN pip install ... /bin/bash: line 1: pip: command not found`

**Causa**: Un `nixpacks.toml` personalizado sobreescribe la fase `setup` y Nixpacks no instala Python.

**Solución**: No usar `nixpacks.toml`. Configurar el build en `railway.toml` con `buildCommand` y dejar que Nixpacks maneje la instalación de Python automáticamente.

### Problema: `FileNotFoundError: /app/logs/errors.log`

**Síntomas**: Crash al iniciar Django con `ValueError: Unable to configure handler 'error_file'`

**Causa**: `base.py` define `RotatingFileHandler` que escribe a `logs/errors.log` y `logs/info.log`. En Railway la carpeta `/app/logs/` no existe. Django falla al inicializar logging antes de ejecutar cualquier comando.

**Solución**: No usar file handlers en `base.py`. Solo `StreamHandler` (console). Railway captura stdout automáticamente. Los file handlers solo deben existir en `development.py` para uso local.

### Problema: Health Check Devuelve 301

**Síntomas**: Logs muestran `GET /health/live/ HTTP/1.1" 301` y el health check falla cíclicamente.

**Causa**: `SECURE_SSL_REDIRECT = True` redirige todo HTTP a HTTPS. Railway hace health checks internamente por HTTP plano. Django responde 301, Railway no sigue redirects.

**Solución**: En `production.py`:
```python
SECURE_REDIRECT_EXEMPT = [r'^health/']
```

### Problema: `No directory at: /app/staticfiles/`

**Síntomas**: Warning de WhiteNoise al arrancar. Archivos estáticos no cargan (404).

**Causa**: `collectstatic` no se ejecutó durante el build. Nixpacks no lo ejecuta automáticamente.

**Solución**: En `railway.toml`:
```toml
[build]
buildCommand = "python manage.py collectstatic --noinput --settings=majobacore.settings.production"
```

### Problema: Deployment Falla en Build (dependencias)

**Síntomas**: Error al instalar dependencias

**Solución**:
```bash
# Verificar requirements localmente
pip install -r requirements/production.txt

# Si hay conflictos, generar requirements.txt limpio
pip freeze > requirements.txt
```

### Problema: Migraciones Fallan

**Síntomas**: Error `No such table` o `Relation does not exist`

**Solución**:
```bash
# Ejecutar migraciones manualmente
railway run python manage.py migrate --settings=majobacore.settings.production
```

### Problema: 500 Internal Server Error

**Síntomas**: Página muestra error 500

**Solución**:
1. Verificar logs en Railway:
   ```bash
   railway logs
   ```

2. Verificar variables de entorno:
   ```bash
   railway variables
   ```

3. Verificar SECRET_KEY está configurado

4. Verificar ALLOWED_HOSTS incluye tu dominio

### Problema: Archivos Estáticos No Cargan

**Síntomas**: CSS/JS/Imágenes devuelven 404

**Solución**:
```bash
# Ejecutar collectstatic manualmente
railway run python manage.py collectstatic --noinput --settings=majobacore.settings.production
```

Verificar en `railway.json` que el build incluye `collectstatic`.

### Problema: Redis No Conecta

**Síntomas**: Error al guardar sesiones

**Solución**:
1. Verificar que Redis está corriendo:
   - Ve a tu servicio Redis en Railway
   - Check que está "Active"

2. Verificar `REDIS_URL`:
   ```bash
   railway variables
   ```

3. Verificar que la variable usa la referencia correcta:
   ```bash
   REDIS_URL=${{Redis.REDIS_URL}}
   ```

### Problema: Base de Datos No Conecta

**Síntomas**: Error `could not connect to server`

**Solución**:
1. Verificar que PostgreSQL está corriendo

2. Verificar variables de base de datos:
   ```bash
   railway variables
   ```

3. Verificar que usas las referencias correctas:
   ```bash
   DB_NAME=${{Postgres.PGDATABASE}}
   DB_USER=${{Postgres.PGUSER}}
   # etc.
   ```

### Problema: CSRF Verification Failed

**Síntomas**: Error al enviar formularios

**Solución**:
1. Agregar dominio a `CSRF_TRUSTED_ORIGINS`:
   ```bash
   CSRF_TRUSTED_ORIGINS=https://tu-app.railway.app
   ```

2. Verificar que `CSRF_COOKIE_SECURE=True` solo en producción

### Problema: Too Many Requests (429)

**Síntomas**: Railway bloquea requests

**Solución**:
Railway tiene límites de rate limiting. Considera:
- Upgrade a plan pago
- Implementar caching más agresivo
- Optimizar queries de base de datos

---

## 📚 Comandos Útiles

### Railway CLI

```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Linkar proyecto
railway link

# Ver variables
railway variables

# Agregar variable
railway variables set SECRET_KEY=valor

# Ver logs
railway logs

# Ejecutar comando en producción
railway run python manage.py <comando>

# Abrir shell de Django
railway run python manage.py shell

# Crear superusuario
railway run python manage.py createsuperuser

# Ver status
railway status

# Abrir dashboard
railway open
```

### Django Management Commands

```bash
# Validar configuración de producción
railway run python manage.py check_production_settings

# Verificar deployment checks
railway run python manage.py check --deploy

# Ver migraciones
railway run python manage.py showmigrations

# Generar nuevo SECRET_KEY
railway run python manage.py generate_secret_key

# Flush database (cuidado!)
railway run python manage.py flush
```

---

## 🎯 Checklist Final

Antes de considerar el deployment completo, verifica:

### Pre-Deployment
- [ ] Código en GitHub actualizado
- [ ] SECRET_KEY generado y guardado
- [ ] Variables de entorno documentadas
- [ ] Tests pasando localmente
- [ ] `requirements.txt` en la raíz (apunta a `requirements/production.txt`)
- [ ] `runtime.txt` con versión de Python
- [ ] `railway.toml` con `buildCommand` para `collectstatic`
- [ ] `Procfile` con comando `web:` (migrate + gunicorn)
- [ ] NO existe `nixpacks.toml` (evitar conflictos con detección automática)

### Deployment
- [ ] PostgreSQL agregado y conectado
- [ ] Redis agregado y conectado (opcional, tiene fallback a LocMemCache)
- [ ] Variables de entorno configuradas
- [ ] Build exitoso (collectstatic se ejecutó)
- [ ] Migraciones aplicadas
- [ ] Gunicorn corriendo en `$PORT`

### Post-Deployment
- [ ] Health check (`/health/live/`) responde 200 (no 301)
- [ ] Página principal carga
- [ ] Admin accesible
- [ ] Superusuario creado
- [ ] Login funciona
- [ ] Archivos estáticos cargan (no hay warning de WhiteNoise)
- [ ] CSRF funciona
- [ ] Cache funciona
- [ ] Logs sin errores críticos
- [ ] Sentry configurado (opcional)

### Seguridad
- [ ] DEBUG=False
- [ ] SECRET_KEY único y seguro
- [ ] ALLOWED_HOSTS configurado (incluye dominio Railway)
- [ ] HTTPS habilitado (`SECURE_SSL_REDIRECT=True`)
- [ ] `SECURE_REDIRECT_EXEMPT = [r'^health/']` configurado
- [ ] Cookies seguras habilitadas (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- [ ] CSRF_TRUSTED_ORIGINS incluye `https://tu-app.railway.app`
- [ ] HSTS configurado
- [ ] CSP configurado
- [ ] Logging solo a stdout (sin file handlers en producción)

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** en Railway Dashboard
2. **Consulta la documentación** de Railway: https://docs.railway.app/
3. **Ejecuta el validador**:
   ```bash
   railway run python manage.py check_production_settings
   ```

---

## 🎉 ¡Éxito!

Si completaste todos los pasos, tu aplicación MajobaSyS debería estar corriendo en producción de manera segura y optimizada.

**Próximos pasos:**
- Configurar dominio personalizado
- Implementar CI/CD con GitHub Actions
- Configurar monitoreo avanzado
- Implementar backups automáticos
- Optimizar performance con CDN

---

**Documentación generada**: Febrero 2026  
**Última actualización**: 2026-02-22 (fixes de Nixpacks, logging, SSL redirect, staticfiles)  
**Versión**: 1.1.0
