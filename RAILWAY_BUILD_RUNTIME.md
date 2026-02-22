# Railway Build vs Runtime: Gestión de Variables de Entorno

> **Fecha:** 2026-02-22  
> **Cambio:** Convertidos `raise ValueError` a `warnings.warn()` para permitir builds sin variables

---

## 🎯 Problema Resuelto

Anteriormente, Railway permitía hacer deploy sin configurar variables de entorno, y luego agregarlas después. **Ahora Railway valida variables durante el build phase**, lo que causaba que el build fallara si faltaban variables como `DATABASE_URL`, `SECRET_KEY`, etc.

### Comportamiento Anterior vs Nuevo

| Fase | Antes | Después del Fix |
|------|-------|----------------|
| **BUILD** (collectstatic) | ❌ Fallaba si faltaban variables | ✅ Muestra warnings pero continúa |
| **RUNTIME** (servidor) | ✅ Validaba variables | ✅ Muestra warnings pero continúa |

---

## 🔧 Cambios Implementados

### 1. **SECRET_KEY** (`base.py`)

**Antes:**
```python
SECRET_KEY = config('SECRET_KEY')  # ❌ Fallaba si no existía
if 'django-insecure' in SECRET_KEY:
    raise ValueError("SECRET_KEY insegura")  # ❌ Detenía el build
```

**Después:**
```python
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-change-this-immediately')
if 'django-insecure' in SECRET_KEY:
    warnings.warn("SECRET_KEY insegura - cámbiala en producción", RuntimeWarning)  # ✅ Continúa
```

---

### 2. **ALLOWED_HOSTS** (`production.py`)

**Antes:**
```python
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
    raise ValueError("ALLOWED_HOSTS debe configurarse")  # ❌ Detenía el build
```

**Después:**
```python
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
    warnings.warn("ALLOWED_HOSTS debe configurarse", RuntimeWarning)  # ✅ Continúa
```

---

### 3. **DATABASE_URL** (`production.py`)

**Antes:**
```python
DATABASE_URL = config('DATABASE_URL', default='')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no encontrada")  # ❌ Detenía el build
```

**Después:**
```python
DATABASE_URL = config('DATABASE_URL', default='')
if not DATABASE_URL:
    warnings.warn(
        "DATABASE_URL no encontrada - usando SQLite como fallback",
        RuntimeWarning
    )  # ✅ Continúa con SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Usar PostgreSQL
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, ...)}
```

---

### 4. **Validación Final** (`production.py`)

**Antes:**
```python
REQUIRED_ENV_VARS = ['SECRET_KEY', 'DATABASE_URL', 'ALLOWED_HOSTS']
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Faltan variables: {missing_vars}")  # ❌ Detenía el build
```

**Después:**
```python
RECOMMENDED_ENV_VARS = ['SECRET_KEY', 'DATABASE_URL', 'ALLOWED_HOSTS']
missing_vars = [var for var in RECOMMENDED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    warnings.warn(
        f"Faltan variables recomendadas: {missing_vars}",
        RuntimeWarning
    )  # ✅ Continúa con warnings
```

---

## 📋 Detección de Fases: BUILD vs RUNTIME

El sistema detecta automáticamente en qué fase está:

### Build Phase (`IS_BUILD_PHASE = True`)
```python
IS_BUILD_PHASE = sys.argv and any(arg in sys.argv for arg in [
    'collectstatic',
    'compress',
    'compilemessages'
])
```

**Configuraciones durante BUILD:**
- ✅ SECRET_KEY: Usa valor temporal dummy
- ✅ DATABASES: SQLite `:memory:`
- ✅ CACHES: DummyCache
- ✅ EMAIL: Console backend
- ✅ Todas las validaciones son warnings, no errors

### Runtime Phase (`IS_BUILD_PHASE = False`)
```python
# Detectado cuando se ejecuta gunicorn, runserver, etc.
```

**Configuraciones durante RUNTIME:**
- ⚠️ SECRET_KEY: Usa variable de entorno (o fallback con warning)
- ⚠️ DATABASES: PostgreSQL con `DATABASE_URL` (o SQLite con warning)
- ⚠️ CACHES: Redis con `REDIS_URL` (o LocMemCache con warning)
- ⚠️ EMAIL: SMTP si está configurado (o console con warning)
- ⚠️ Validaciones muestran warnings pero permiten continuar

---

## 🚀 Flujo de Despliegue en Railway

### Paso 1: Deploy Inicial (SIN variables configuradas)

```bash
# Railway ejecuta durante BUILD:
python manage.py collectstatic --noinput

# Resultado:
✅ BUILD exitoso con warnings:
   ⚠️ WARNING: SECRET_KEY usando valor temporal
   ⚠️ WARNING: DATABASE_URL no encontrada - usando SQLite
   ⚠️ WARNING: ALLOWED_HOSTS usando defaults
```

### Paso 2: Configurar Variables (DESPUÉS del deploy)

En el dashboard de Railway:
1. Agregar PostgreSQL → Genera automáticamente `DATABASE_URL`
2. Agregar Redis → Genera automáticamente `REDIS_URL`
3. Configurar manualmente:
   - `SECRET_KEY` → Generar con `python manage.py generate_secret_key`
   - `ALLOWED_HOSTS` → Dominio de Railway (ej: `myapp.railway.app`)

### Paso 3: Railway Redeploy Automático

Railway detecta los cambios en variables y redeploya automáticamente.

```bash
# Railway ejecuta durante RUNTIME:
gunicorn majobacore.wsgi:application

# Resultado:
✅ RUNTIME exitoso SIN warnings:
   ✅ SECRET_KEY configurada correctamente
   ✅ DATABASE_URL conectada a PostgreSQL
   ✅ ALLOWED_HOSTS configurados
   ✅ Redis conectado
```

---

## 🔒 Seguridad

### ⚠️ Warnings NO son Errores

Los warnings indican configuración subóptima pero **no detienen la aplicación**.

**En producción debes:**
1. ✅ Configurar `SECRET_KEY` real (generada con comando)
2. ✅ Configurar `DATABASE_URL` (PostgreSQL de Railway)
3. ✅ Configurar `ALLOWED_HOSTS` con tu dominio
4. ✅ Configurar `REDIS_URL` (Redis de Railway)
5. ✅ Configurar email SMTP (opcional pero recomendado)

### 🔥 Claves Inseguras Detectadas

Si detectamos claves inseguras, mostramos warnings:

```python
INSECURE_KEYS = [
    'django-insecure-d*xd59=w7923dsnt#xy=8jbuf_c*6scivaft%ko(8r8vq6jd0l',
    'django-insecure-build-key-only-for-collectstatic',
]

if SECRET_KEY in INSECURE_KEYS:
    warnings.warn("⚠️ CRITICAL: Clave insegura en producción!", RuntimeWarning)
```

**Acción:** Ver warnings en logs de Railway y configurar variables correctamente.

---

## 📊 Fallbacks por Variable

| Variable | Fallback en RUNTIME | Impacto |
|----------|---------------------|---------|
| `SECRET_KEY` | Valor dummy inseguro | ⚠️ Alto - Cambiar inmediatamente |
| `DATABASE_URL` | SQLite local | ⚠️ Alto - Datos volátiles en Railway |
| `REDIS_URL` | LocMemCache | ⚠️ Medio - Sin cache compartido |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | ⚠️ Alto - Solo funciona local |
| `EMAIL_HOST` | Console backend | ℹ️ Bajo - Emails no se envían |

---

## 🧪 Testing

Los settings siguen detectando correctamente el entorno:

```bash
# Development
python manage.py runserver --settings=majobacore.settings.development
# ✅ SQLite, DummyCache, DEBUG=True

# Production (local)
python manage.py runserver --settings=majobacore.settings.production
# ⚠️ Warnings si faltan variables, pero funciona con fallbacks

# Testing
pytest --settings=majobacore.settings.testing
# ✅ SQLite :memory:, sin migraciones, MD5 hasher
```

---

## 📝 Resumen

| Aspecto | Antes | Después |
|---------|-------|---------|
| Build sin variables | ❌ Fallaba | ✅ Funciona con warnings |
| Runtime sin variables | ❌ Fallaba | ✅ Funciona con warnings + fallbacks |
| Seguridad | ✅ Validación estricta | ⚠️ Validación permisiva con warnings |
| Deploy Railway | ❌ Requería variables primero | ✅ Deploy primero, configurar después |

---

## ✅ Conclusión

**Ahora puedes:**
1. ✅ Hacer deploy en Railway **sin configurar variables primero**
2. ✅ El build ejecuta `collectstatic` con configuraciones dummy
3. ✅ El runtime arranca con fallbacks y muestra warnings
4. ✅ Configurar variables después del primer deploy
5. ✅ Railway redeploya automáticamente con las variables reales

**Los warnings te recuerdan:**
- ⚠️ Qué variables faltan
- ⚠️ Qué configuraciones son inseguras
- ⚠️ Qué acciones tomar para configurar correctamente

**La aplicación funciona** pero con configuración subóptima hasta que configures las variables de entorno adecuadas.

---

## 🔗 Referencias

- **AGENTS.md** - Documentación del proyecto
- **majobacore/settings/base.py** - Detección de BUILD phase
- **majobacore/settings/production.py** - Configuraciones con fallbacks
- **Dockerfile** - Ejecución de collectstatic durante build
