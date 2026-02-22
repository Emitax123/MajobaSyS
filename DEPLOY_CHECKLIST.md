# 🚀 Railway Deploy Checklist - MajobaSyS

> **Última actualización:** 2026-02-22  
> **Status:** ✅ Ready for Deploy

---

## ✅ Pre-Deploy Checklist

### 1. Archivos de Configuración

| Archivo | Status | Verificar |
|---------|--------|-----------|
| ✅ `railway.json` | Configurado | `healthcheckTimeout: 100`, `startCommand` con `$PORT` |
| ✅ `Dockerfile` | Configurado | Usa `$PORT`, sin migraciones en CMD, tiene HEALTHCHECK |
| ✅ `Procfile` | Configurado | `release` phase con migraciones, `web` con gunicorn |
| ✅ `requirements/production.txt` | Actualizado | Todas las dependencias necesarias |
| ✅ `majobacore/settings/production.py` | Configurado | Warnings en vez de errors, fallbacks configurados |
| ✅ `majobacore/views.py` | Configurado | Healthcheck endpoints con `@csrf_exempt` |

---

### 2. Variables de Entorno (Railway)

**CRÍTICAS (Requeridas):**
- [ ] `SECRET_KEY` - Generar con: `python manage.py generate_secret_key`
- [ ] `ALLOWED_HOSTS` - Tu dominio Railway (ej: `myapp.railway.app`)
- [ ] `DJANGO_SETTINGS_MODULE` - `majobacore.settings.production`

**AUTOMÁTICAS (Railway provee):**
- [ ] `PORT` - Railway lo asigna dinámicamente (NO configurar manualmente)
- [ ] `DATABASE_URL` - Al agregar PostgreSQL service
- [ ] `REDIS_URL` - Al agregar Redis service (opcional)

**OPCIONALES:**
- [ ] `EMAIL_HOST` - Para enviar emails (SMTP)
- [ ] `EMAIL_HOST_USER` - Usuario SMTP
- [ ] `EMAIL_HOST_PASSWORD` - Password SMTP
- [ ] `SENTRY_DSN` - Para monitoring de errores (opcional)

---

### 3. Services en Railway

- [ ] **PostgreSQL** - Agregado y conectado (provee `DATABASE_URL` automáticamente)
- [ ] **Redis** - Agregado y conectado (provee `REDIS_URL` automáticamente, opcional)

---

## 🔧 Configuración Correcta

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/health/live/",
    "healthcheckTimeout": 100,
    "startCommand": "gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -"
  }
}
```

### Procfile
```
release: python manage.py migrate --settings=majobacore.settings.production --noinput
web: gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
```

### Dockerfile (Fragmento Clave)
```dockerfile
# PORT dinámico de Railway
EXPOSE $PORT

# Healthcheck interno
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:$PORT/health/live/ || exit 1

# Comando por defecto (Railway override con startCommand)
CMD ["sh", "-c", "gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -"]
```

---

## 🚀 Pasos de Deploy

### Opción A: Deploy desde GitHub

1. **Conectar repositorio a Railway**
   ```
   Railway Dashboard → New Project → Deploy from GitHub
   ```

2. **Agregar PostgreSQL**
   ```
   Railway Dashboard → New → Database → PostgreSQL
   ```

3. **Configurar variables de entorno**
   ```
   Railway Dashboard → Variables → Add Variables:
   - SECRET_KEY: [generar con comando]
   - ALLOWED_HOSTS: myapp.railway.app
   - DJANGO_SETTINGS_MODULE: majobacore.settings.production
   ```

4. **Trigger deploy**
   ```
   Railway auto-deploya al detectar cambios en GitHub
   O manualmente: Deploy → Trigger Deploy
   ```

### Opción B: Deploy desde CLI

1. **Instalar Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login y vincular proyecto**
   ```bash
   railway login
   railway link
   ```

3. **Agregar PostgreSQL**
   ```bash
   railway add --database postgresql
   ```

4. **Configurar variables**
   ```bash
   railway variables set SECRET_KEY="..."
   railway variables set ALLOWED_HOSTS="myapp.railway.app"
   railway variables set DJANGO_SETTINGS_MODULE="majobacore.settings.production"
   ```

5. **Deploy**
   ```bash
   railway up
   ```

---

## 📊 Monitoreo Post-Deploy

### 1. Verificar Deploy Status

**Railway Dashboard:**
- ✅ Status: "Deployment Live" (verde)
- ✅ Healthcheck: "Passing" (verde)
- ✅ Logs: Sin errores críticos

**Logs a buscar:**
```
✅ Listening at: http://0.0.0.0:XXXX (worker with pid XXXX)
✅ Production settings loaded successfully in RUNTIME
✅ Database: django.db.backends.postgresql at postgres.railway.internal
✅ Cache backend: django_redis.cache.RedisCache
```

**Logs a evitar:**
```
❌ Connection refused
❌ Healthcheck failed
❌ ValueError: Missing required environment variables
❌ Listening at: http://0.0.0.0:8000 (incorrecto, debe ser $PORT)
```

---

### 2. Verificar Endpoints Públicamente

**Healthcheck:**
```bash
curl https://myapp.railway.app/health/live/
# Respuesta esperada: OK

curl https://myapp.railway.app/health/ready/
# Respuesta esperada: Ready
```

**Landing Page:**
```bash
curl -I https://myapp.railway.app/
# HTTP/2 200 (página carga correctamente)
```

**Admin:**
```bash
curl -I https://myapp.railway.app/admin/
# HTTP/2 302 (redirect a login)
```

---

### 3. Verificar Variables de Entorno

**En Railway Dashboard → Variables:**
- ✅ `SECRET_KEY` existe y NO contiene "django-insecure"
- ✅ `ALLOWED_HOSTS` contiene tu dominio Railway
- ✅ `DATABASE_URL` existe (provisto por PostgreSQL service)
- ✅ `PORT` NO existe (Railway lo provee dinámicamente en runtime)

---

## 🐛 Troubleshooting

### Error: "Healthcheck Failed - Connection Refused"

**Causa:** Gunicorn no está escuchando en el puerto correcto.

**Solución:**
1. Verificar que Dockerfile/Procfile usan `$PORT` (no `8000`)
2. Verificar logs: `Listening at: http://0.0.0.0:XXXX`
3. NO configurar `PORT` en variables de entorno (Railway lo provee)

---

### Error: "Healthcheck Timeout"

**Causa:** La aplicación tarda más de 100s en arrancar.

**Solución:**
1. Verificar que migraciones están en `release` phase (Procfile), no en CMD
2. Revisar logs para ver qué está tardando
3. Si necesario, aumentar `healthcheckTimeout` en railway.json

---

### Error: "503 Service Unavailable"

**Causa:** Database no conectada o healthcheck verifica DB muy temprano.

**Solución:**
1. Verificar que PostgreSQL service está agregado
2. Verificar `DATABASE_URL` en variables
3. Usar `/health/live/` (no verifica DB) en vez de `/health/ready/`

---

### Error: "403 Forbidden" en Healthcheck

**Causa:** CSRF protection bloqueando Railway healthcheck.

**Solución:**
1. Verificar que healthcheck endpoints tienen `@csrf_exempt`
2. Verificar que `railway.json` apunta a `/health/live/`

---

### Warning: "SECRET_KEY insegura"

**Causa:** Variable `SECRET_KEY` no configurada o contiene "django-insecure".

**Solución:**
```bash
# Generar SECRET_KEY
python manage.py generate_secret_key

# Configurar en Railway
railway variables set SECRET_KEY="[clave generada]"
```

---

### Warning: "DATABASE_URL not found - using SQLite"

**Causa:** PostgreSQL service no agregado o no conectado.

**Solución:**
```bash
# Agregar PostgreSQL
railway add --database postgresql

# Verificar conexión
railway variables get DATABASE_URL
```

---

## 🔐 Post-Deploy Security Checklist

- [ ] `SECRET_KEY` es único y seguro (no contiene "django-insecure")
- [ ] `ALLOWED_HOSTS` solo contiene dominios confiables
- [ ] `DEBUG=False` (verificar en logs: "DEBUG mode: False")
- [ ] `DATABASE_URL` usa PostgreSQL (no SQLite)
- [ ] HTTPS está activado (Railway lo provee automáticamente)
- [ ] Admin URL es accesible solo con autenticación
- [ ] Static files se sirven correctamente (WhiteNoise)

---

## 📋 Comandos Útiles Railway CLI

```bash
# Ver logs en tiempo real
railway logs

# Ver variables de entorno
railway variables

# Ejecutar comando en el contenedor
railway run python manage.py createsuperuser

# Abrir shell en el contenedor
railway shell

# Ver status del deploy
railway status

# Redeploy
railway redeploy

# Abrir en navegador
railway open
```

---

## ✅ Deploy Exitoso

**Indicadores de éxito:**
- ✅ Railway Dashboard muestra "Deployment Live" (verde)
- ✅ Healthcheck pasa (verde)
- ✅ `https://myapp.railway.app/` carga la landing page
- ✅ `https://myapp.railway.app/health/live/` responde "OK"
- ✅ Logs muestran: "Listening at: http://0.0.0.0:$PORT"
- ✅ Sin warnings críticos en logs
- ✅ Admin es accesible en `/admin/`

---

## 📚 Documentación de Referencia

- **RAILWAY_HEALTHCHECK_FIX.md** - Fix detallado del healthcheck
- **RAILWAY_BUILD_RUNTIME.md** - Sistema BUILD vs RUNTIME
- **CHANGELOG_BUILD_FIX.md** - Changelog de cambios
- **AGENTS.md** - Documentación completa del proyecto

---

## 🎉 ¡Listo para Deploy!

Si todos los checkboxes están marcados, tu aplicación está lista para desplegarse en Railway sin problemas.

**Comando final:**
```bash
git add .
git commit -m "Fix Railway healthcheck and build configuration"
git push railway main
```

Railway detectará los cambios y auto-desplegará con la nueva configuración. El healthcheck ahora debería pasar correctamente.
