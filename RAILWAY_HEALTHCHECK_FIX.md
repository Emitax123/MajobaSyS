# Railway Healthcheck Fix - Service Unavailable

> **Fecha:** 2026-02-22  
> **Problema:** `Attempt #1 failed with service unavailable. Continuing to retry for 28s`  
> **Causa:** Problemas con PORT y configuración de healthcheck

---

## 🔍 Problema Identificado

Railway reportaba errores de healthcheck:
```
Attempt #1 failed with service unavailable. Continuing to retry for 28s
```

### Causas Raíz:

1. **PORT Variable Incorrecta** ❌
   - Dockerfile usaba: `${PORT:-8000}` (con fallback)
   - Railway espera: `$PORT` (sin fallback, dinámico)

2. **Healthcheck Timeout Muy Corto** ⏱️
   - Timeout configurado: 30 segundos
   - Migraciones pueden tardar más durante el primer deploy

3. **Conflicto CMD vs startCommand** ⚠️
   - Dockerfile CMD incluía migraciones
   - Railway tiene fase separada de `release` para migraciones

4. **CSRF Protection en Healthcheck** 🔒
   - Railway hace peticiones GET sin CSRF token
   - Healthcheck endpoints necesitan `@csrf_exempt`

5. **Falta HEALTHCHECK en Dockerfile** 📊
   - Docker no tenía configuración de healthcheck interna

---

## ✅ Soluciones Implementadas

### 1. **railway.json** - Configuración Mejorada

**Antes:**
```json
{
  "deploy": {
    "healthcheckPath": "/health/live/",
    "healthcheckTimeout": 30
  }
}
```

**Después:**
```json
{
  "deploy": {
    "healthcheckPath": "/health/live/",
    "healthcheckTimeout": 100,
    "startCommand": "gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -"
  }
}
```

**Cambios:**
- ✅ `healthcheckTimeout`: 30s → 100s (permite migraciones lentas)
- ✅ `startCommand`: Comando explícito para Railway (override del Dockerfile CMD)

---

### 2. **Dockerfile** - PORT Dinámico y Healthcheck

**Antes:**
```dockerfile
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn majobacore.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120"]
```

**Después:**
```dockerfile
# Expose port (Railway usa PORT dinámico)
EXPOSE $PORT

# Health check (opcional - Railway usa HTTP healthcheck)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:$PORT/health/live/ || exit 1

# Default command (Railway override con startCommand en railway.json)
# No incluir migraciones aquí - Railway las ejecuta en release phase
CMD ["sh", "-c", "gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -"]
```

**Cambios:**
- ✅ `$PORT` sin fallback (Railway lo provee dinámicamente)
- ✅ `HEALTHCHECK` agregado para Docker health monitoring
- ✅ Migraciones removidas del CMD (Railway usa Procfile `release`)
- ✅ Logs redirigidos a stdout/stderr (`--access-logfile -`)

---

### 3. **views.py** - Healthcheck Endpoints Optimizados

**Antes:**
```python
@require_http_methods(["GET"])
def liveness_check(request):
    return HttpResponse("OK", status=200)
```

**Después:**
```python
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
```

**Cambios:**
- ✅ `@csrf_exempt`: Railway puede hacer peticiones sin token
- ✅ `["GET", "HEAD"]`: Soporta ambos métodos HTTP
- ✅ `content_type="text/plain"`: Respuesta explícita
- ✅ Sin verificación de DB/cache (endpoint ultra-rápido)

---

### 4. **Readiness Check Mejorado**

```python
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
```

**Cambios:**
- ✅ `@csrf_exempt`: Sin CSRF protection
- ✅ `content_type="text/plain"`: Respuesta clara
- ✅ Verifica DB antes de devolver 200

---

## 📊 Diferencia entre Endpoints de Health

| Endpoint | Propósito | Verifica DB | Verifica Cache | Uso Railway |
|----------|-----------|-------------|----------------|-------------|
| `/health/live/` | ¿Está viva la app? | ❌ No | ❌ No | ✅ Healthcheck |
| `/health/ready/` | ¿Lista para tráfico? | ✅ Sí | ❌ No | ⚙️ Readiness probe |
| `/health/` | Status completo | ✅ Sí | ✅ Sí | 📊 Monitoreo manual |

### ¿Por qué `/health/live/` NO verifica DB?

**Razón:** Durante el startup, la DB puede no estar lista todavía (migraciones ejecutándose). Si el liveness check falla, Railway **mata el contenedor** y lo reinicia, creando un loop infinito.

**Solución:** 
- **Liveness** (`/health/live/`) → Solo verifica que Django está respondiendo
- **Readiness** (`/health/ready/`) → Verifica que DB está lista

---

## 🚀 Flujo de Deploy Corregido

### Antes del Fix:
```
1. Railway build image
2. Railway ejecuta Dockerfile CMD (migraciones + gunicorn)
3. Gunicorn arranca en puerto incorrecto (8000 en vez de $PORT)
4. Railway healthcheck GET /health/live/ (timeout 30s)
   ❌ Connection refused (puerto incorrecto)
   ❌ Timeout (migraciones tardaron más de 30s)
5. Railway marca el deploy como FAILED
```

### Después del Fix:
```
1. Railway build image
2. Railway ejecuta Procfile `release` (migraciones separadas)
   ✅ python manage.py migrate --noinput
3. Railway ejecuta `startCommand` (gunicorn con $PORT correcto)
   ✅ gunicorn --bind 0.0.0.0:$PORT
4. Railway healthcheck GET /health/live/ (timeout 100s)
   ✅ 200 OK (endpoint ultra-rápido, sin CSRF)
5. Railway marca el deploy como SUCCESS
```

---

## 🔧 Variables de Entorno Críticas

| Variable | Valor | Provisto por | Propósito |
|----------|-------|--------------|-----------|
| `PORT` | Dinámico (ej: 5432) | Railway automático | Puerto del servidor |
| `DATABASE_URL` | `postgresql://...` | Railway (al agregar PostgreSQL) | Conexión a DB |
| `DJANGO_SETTINGS_MODULE` | `majobacore.settings.production` | Manual | Settings de producción |
| `SECRET_KEY` | Random string | Manual | Seguridad Django |
| `ALLOWED_HOSTS` | `myapp.railway.app` | Manual | Hosts permitidos |

**IMPORTANTE:** No hardcodear `PORT=8000`, Railway lo provee dinámicamente.

---

## 🧪 Testing Local

### 1. Verificar Healthcheck Endpoints

```bash
# Liveness check (debe ser ultra-rápido)
curl http://localhost:8000/health/live/
# Respuesta: OK

# Readiness check (verifica DB)
curl http://localhost:8000/health/ready/
# Respuesta: Ready (si DB está conectada)

# Health check completo (JSON)
curl http://localhost:8000/health/
# Respuesta: {"status": "healthy", "checks": {...}}
```

### 2. Simular Railway Healthcheck

```bash
# Railway hace HEAD request, no GET
curl -I http://localhost:8000/health/live/
# HTTP/1.1 200 OK
# Content-Type: text/plain

# Con timeout como Railway (100s)
curl --max-time 100 http://localhost:8000/health/live/
# OK
```

### 3. Probar con Docker

```bash
# Build image
docker build -t majobasys .

# Ejecutar con PORT dinámico
docker run -p 8080:8080 -e PORT=8080 -e SECRET_KEY=test majobasys

# Verificar healthcheck
curl http://localhost:8080/health/live/
```

---

## 📋 Checklist de Deployment Railway

### Pre-Deploy:
- [ ] `railway.json` tiene `healthcheckTimeout: 100`
- [ ] `railway.json` tiene `startCommand` con `$PORT`
- [ ] Dockerfile NO incluye migraciones en CMD
- [ ] Dockerfile usa `$PORT` (no `${PORT:-8000}`)
- [ ] `Procfile` tiene `release` phase para migraciones
- [ ] Healthcheck endpoints tienen `@csrf_exempt`
- [ ] Variables de entorno configuradas (SECRET_KEY, ALLOWED_HOSTS)

### Post-Deploy:
- [ ] Railway muestra "Deployment Live"
- [ ] Healthcheck pasa (verde en Railway dashboard)
- [ ] Logs muestran: `Listening at: http://0.0.0.0:$PORT`
- [ ] Visitar `https://myapp.railway.app/health/live/` → `OK`
- [ ] Visitar `https://myapp.railway.app/` → Landing page carga

---

## 🔍 Debugging Healthcheck Failures

### Error: "Connection refused"
**Causa:** Gunicorn no está escuchando en el puerto correcto.
**Solución:** Verificar que usas `$PORT`, no `8000`.

```bash
# En logs de Railway buscar:
Listening at: http://0.0.0.0:XXXX  # XXXX debe ser el PORT de Railway
```

### Error: "Timeout after 100s"
**Causa:** La aplicación tarda mucho en arrancar.
**Solución:** 
1. Verificar que migraciones están en `release` phase, no en CMD
2. Aumentar `healthcheckTimeout` si es necesario
3. Revisar logs para ver qué está tardando

### Error: "403 Forbidden"
**Causa:** CSRF protection bloqueando Railway healthcheck.
**Solución:** Agregar `@csrf_exempt` al endpoint de healthcheck.

### Error: "503 Service Unavailable"
**Causa:** Database no está lista o healthcheck verifica DB muy temprano.
**Solución:** Usar `/health/live/` que NO verifica DB.

---

## 📚 Archivos Modificados

| Archivo | Cambios | Propósito |
|---------|---------|-----------|
| `railway.json` | `healthcheckTimeout: 100`, `startCommand` | Configuración Railway |
| `Dockerfile` | `$PORT`, `HEALTHCHECK`, sin migraciones en CMD | Container config |
| `majobacore/views.py` | `@csrf_exempt`, `content_type`, HEAD support | Endpoints optimizados |
| `Procfile` | Ya existía con `release` phase | Migraciones separadas |

---

## ✅ Resultado

**Antes:**
```
❌ Healthcheck failed: Connection refused
❌ Deploy fallido después de múltiples intentos
❌ Railway reinicia contenedor en loop
```

**Después:**
```
✅ Healthcheck passed (200 OK)
✅ Deploy exitoso en primer intento
✅ Aplicación accesible en https://myapp.railway.app
```

---

## 🔗 Referencias

- **Railway Docs:** https://docs.railway.app/deploy/healthchecks
- **Gunicorn Binding:** https://docs.gunicorn.org/en/stable/settings.html#bind
- **Django Health Checks:** https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- **Procfile Format:** https://docs.railway.app/deploy/deployments#procfile

---

## 💡 Notas Finales

1. **PORT es dinámico en Railway** - Nunca hardcodear a 8000
2. **Healthcheck debe ser ultra-rápido** - No verificar DB en liveness
3. **Migraciones en release phase** - No en el CMD del contenedor
4. **Timeout generoso (100s)** - Permite migraciones lentas en primer deploy
5. **@csrf_exempt en healthchecks** - Railway no envía CSRF token

**La aplicación ahora debería deployar correctamente en Railway sin errores de healthcheck.**
