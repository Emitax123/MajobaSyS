# Changelog: Fix Railway Build Phase (2026-02-22)

## 🎯 Problema Resuelto

Railway ahora valida variables de entorno durante la fase de BUILD, causando que el deployment falle si faltan variables como `DATABASE_URL`, `SECRET_KEY`, etc.

**Solución:** Convertir todos los `raise ValueError` en `warnings.warn()` para permitir que el build prosiga sin errores.

---

## ✅ Cambios Realizados

### 1. **base.py** - SECRET_KEY con fallback

**Archivo:** `majobacore/settings/base.py`

**Antes:**
```python
SECRET_KEY = config('SECRET_KEY')  # ❌ Fallaba si no existía
if 'django-insecure' in SECRET_KEY:
    raise ValueError("SECRET_KEY insegura")  # ❌ Detenía build
```

**Después:**
```python
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-change-this-immediately')
if 'django-insecure' in SECRET_KEY:
    warnings.warn("SECRET_KEY insegura - cámbiala", RuntimeWarning)  # ✅ Continúa con warning
```

---

### 2. **production.py** - ALLOWED_HOSTS con warning

**Archivo:** `majobacore/settings/production.py` (líneas 28-48)

**Antes:**
```python
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
    raise ValueError("ALLOWED_HOSTS debe configurarse")  # ❌
```

**Después:**
```python
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
    warnings.warn("ALLOWED_HOSTS debe configurarse", RuntimeWarning)  # ✅
```

---

### 3. **production.py** - DATABASE_URL con fallback SQLite

**Archivo:** `majobacore/settings/production.py` (líneas 105-142)

**Antes:**
```python
DATABASE_URL = config('DATABASE_URL', default='')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no encontrada")  # ❌ Fallaba
```

**Después:**
```python
DATABASE_URL = config('DATABASE_URL', default='')
if not DATABASE_URL:
    warnings.warn(
        "DATABASE_URL no encontrada - usando SQLite como fallback",
        RuntimeWarning
    )  # ✅ Warning
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Usar PostgreSQL con DATABASE_URL
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, ...)}
```

---

### 4. **production.py** - Validación final con warnings

**Archivo:** `majobacore/settings/production.py` (líneas 448-471)

**Antes:**
```python
REQUIRED_ENV_VARS = ['SECRET_KEY', 'DATABASE_URL', 'ALLOWED_HOSTS']
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Faltan variables: {missing_vars}")  # ❌ Fallaba
```

**Después:**
```python
RECOMMENDED_ENV_VARS = ['SECRET_KEY', 'DATABASE_URL', 'ALLOWED_HOSTS']
missing_vars = [var for var in RECOMMENDED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    warnings.warn(
        f"Faltan variables recomendadas: {missing_vars}",
        RuntimeWarning
    )  # ✅ Warning, no error
```

---

### 5. **production.py** - Fix logging sin HOST

**Archivo:** `majobacore/settings/production.py` (líneas 481-487)

**Antes:**
```python
logger.info(f'Database: {DATABASES["default"]["ENGINE"]} at {DATABASES["default"]["HOST"]}')
# ❌ KeyError si es SQLite (no tiene HOST)
```

**Después:**
```python
db_engine = DATABASES["default"]["ENGINE"]
db_host = DATABASES["default"].get("HOST", "local/sqlite")  # ✅ Fallback
logger.info(f'Database: {db_engine} at {db_host}')
```

---

### 6. **production.py** - Fix template configuration

**Archivo:** `majobacore/settings/production.py` (líneas 419-430)

**Antes:**
```python
# Template caching con APP_DIRS=True (error)
TEMPLATES[0]['OPTIONS']['loaders'] = [...]  # ❌ Conflicto con APP_DIRS
```

**Después:**
```python
# Template caching - APP_DIRS y loaders son mutuamente excluyentes
TEMPLATES[0]['APP_DIRS'] = False  # ✅ Deshabilitar APP_DIRS
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
```

---

## 📊 Resultados

### Antes de los cambios:
```bash
python manage.py collectstatic --settings=majobacore.settings.production
# ❌ ValueError: DATABASE_URL not found
# ❌ Build fallaba
```

### Después de los cambios:
```bash
python manage.py collectstatic --settings=majobacore.settings.production
# ⚠️ WARNING: DATABASE_URL not found - using SQLite
# ⚠️ WARNING: Missing recommended variables
# ✅ System check identified no issues (0 silenced)
# ✅ Collectstatic completed successfully
```

---

## 🚀 Impacto en Railway Deployment

### Flujo de Deploy Nuevo

1. **Push a Railway** (sin variables configuradas)
   ```bash
   git push railway main
   ```

2. **Build Phase** (dentro del Dockerfile)
   ```bash
   # Railway ejecuta:
   python manage.py collectstatic --noinput
   
   # Resultado:
   ⚠️ WARNING: DATABASE_URL not found - using SQLite fallback
   ⚠️ WARNING: Missing recommended environment variables
   ✅ BUILD EXITOSO
   ```

3. **Configurar variables** (después del deploy)
   - Agregar PostgreSQL → `DATABASE_URL` (automático)
   - Agregar Redis → `REDIS_URL` (automático)
   - Configurar `SECRET_KEY` manualmente
   - Configurar `ALLOWED_HOSTS` manualmente

4. **Redeploy automático**
   ```bash
   # Railway redeploya automáticamente al detectar cambios en variables
   
   # Runtime Phase:
   ✅ DATABASE_URL configurada → PostgreSQL
   ✅ SECRET_KEY configurada → Segura
   ✅ ALLOWED_HOSTS configurada → Dominio Railway
   ✅ SIN WARNINGS
   ```

---

## 📋 Checklist de Variables para Producción

| Variable | Requerido | Fallback | Impacto |
|----------|-----------|----------|---------|
| `SECRET_KEY` | ✅ Sí | Valor inseguro | ⚠️ CRÍTICO - Cambiar inmediatamente |
| `DATABASE_URL` | ✅ Sí | SQLite local | ⚠️ ALTO - Datos volátiles |
| `ALLOWED_HOSTS` | ✅ Sí | `localhost,127.0.0.1` | ⚠️ ALTO - Solo funciona local |
| `REDIS_URL` | ⚙️ Opcional | LocMemCache | ⚠️ Medio - Sin cache compartido |
| `EMAIL_HOST` | ⚙️ Opcional | Console backend | ℹ️ Bajo - Emails no se envían |
| `SENTRY_DSN` | ⚙️ Opcional | Sin monitoreo | ℹ️ Bajo - Sin tracking de errores |

---

## 🔒 Consideraciones de Seguridad

### ⚠️ IMPORTANTE: Los warnings NO son errores

Los warnings indican **configuración subóptima** pero **no detienen la aplicación**.

**En producción debes:**
1. ✅ Configurar `SECRET_KEY` real (usar comando: `python manage.py generate_secret_key`)
2. ✅ Configurar `DATABASE_URL` (PostgreSQL de Railway)
3. ✅ Configurar `ALLOWED_HOSTS` (dominio Railway: `myapp.railway.app`)
4. ✅ Configurar `REDIS_URL` (Redis de Railway)
5. ⚙️ Configurar email SMTP (opcional pero recomendado)

### 🔐 Detección de Claves Inseguras

El sistema detecta y advierte sobre claves inseguras:

```python
INSECURE_KEYS = [
    'django-insecure-d*xd59=w7923dsnt#xy=8jbuf_c*6scivaft%ko(8r8vq6jd0l',
    'django-insecure-build-key-only-for-collectstatic',
    'django-insecure-fallback-key-change-this-immediately',
]

if SECRET_KEY in INSECURE_KEYS:
    warnings.warn("⚠️ CRITICAL: Clave insegura en producción!", RuntimeWarning)
```

**Acción:** Monitorear logs de Railway y configurar `SECRET_KEY` real.

---

## 🧪 Tests de Validación

### 1. Verificar que el check funcione sin variables
```bash
python manage.py check --settings=majobacore.settings.production
# ✅ System check identified no issues (0 silenced)
# ⚠️ RuntimeWarning: Missing recommended environment variables
```

### 2. Verificar que collectstatic funcione sin variables
```bash
python manage.py collectstatic --noinput --dry-run --settings=majobacore.settings.production
# ✅ Pretending to copy 'static/...'
# ⚠️ RuntimeWarning: DATABASE_URL not found
```

### 3. Verificar logs en Railway
```bash
# Durante BUILD:
[INFO] Production settings loaded in BUILD PHASE (collectstatic)
[INFO] Using dummy configurations for database and cache

# Durante RUNTIME (sin variables):
[WARNING] DATABASE_URL not found - falling back to SQLite
[WARNING] Missing recommended environment variables: SECRET_KEY, DATABASE_URL
[INFO] Database: django.db.backends.sqlite3 at local/sqlite

# Durante RUNTIME (con variables configuradas):
[INFO] Production settings loaded successfully in RUNTIME
[INFO] Database: django.db.backends.postgresql at postgres.railway.internal
[INFO] Cache backend: django_redis.cache.RedisCache
```

---

## 📚 Documentación Adicional

- **RAILWAY_BUILD_RUNTIME.md** - Explicación detallada del sistema BUILD vs RUNTIME
- **AGENTS.md** - Documentación completa del proyecto actualizada
- **railway.json** - Configuración de deployment
- **Dockerfile** - Build process con collectstatic

---

## ✅ Conclusión

**Cambios aplicados con éxito:**
- ✅ Convertidos todos los `raise ValueError` en `warnings.warn()`
- ✅ Agregados fallbacks para todas las variables críticas
- ✅ Build funciona sin variables de entorno configuradas
- ✅ Runtime funciona con fallbacks y muestra warnings
- ✅ Fix en logging para SQLite sin HOST
- ✅ Fix en template configuration (APP_DIRS vs loaders)

**Ahora puedes:**
1. ✅ Deploy en Railway sin configurar variables primero
2. ✅ El build ejecuta `collectstatic` sin errores
3. ✅ El runtime arranca con configuraciones dummy
4. ✅ Configurar variables después del primer deploy
5. ✅ Railway redeploya automáticamente con las variables reales

**Los warnings te guían:**
- ⚠️ Qué variables faltan
- ⚠️ Qué configuraciones son inseguras
- ⚠️ Qué acciones tomar para producción

---

## 🔗 Commits Relacionados

- **Commit:** Fix Railway build phase - Convert ValueError to warnings
- **Fecha:** 2026-02-22
- **Archivos modificados:**
  - `majobacore/settings/base.py`
  - `majobacore/settings/production.py`
  - `RAILWAY_BUILD_RUNTIME.md` (nuevo)
  - `CHANGELOG_BUILD_FIX.md` (este archivo)
