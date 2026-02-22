# Railway Setup Guide - MajobaSyS

## 🚀 Despliegue Simplificado con DATABASE_URL

Este proyecto usa **`DATABASE_URL`** y **`REDIS_URL`** en lugar de múltiples variables separadas.

---

## 📋 Variables de Entorno Requeridas

### ✅ **Mínimas para Iniciar**

Solo necesitas estas 2 variables para el primer deployment:

```env
SECRET_KEY=<genera-con-generate_secret_key>
ALLOWED_HOSTS=<tu-app>.up.railway.app
```

### 🔧 **Railway las Provee Automáticamente**

Cuando agregas servicios en Railway, estas variables se crean automáticamente:

```env
DATABASE_URL=postgresql://user:pass@host:port/dbname  # PostgreSQL
REDIS_URL=redis://default:pass@host:port              # Redis
```

**✨ No necesitas configurar manualmente:** `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

---

## 🛠️ Pasos de Deployment en Railway

### 1️⃣ **Crear Proyecto en Railway**

```bash
# Conectar repositorio GitHub
railway link
```

### 2️⃣ **Agregar PostgreSQL**

1. En Railway Dashboard → **"New" → "Database" → "PostgreSQL"**
2. Railway automáticamente crea la variable `DATABASE_URL`
3. ✅ **No necesitas configurar nada más**

### 3️⃣ **Agregar Redis (Opcional)**

1. En Railway Dashboard → **"New" → "Database" → "Redis"**
2. Railway automáticamente crea la variable `REDIS_URL`
3. Si no agregas Redis, el proyecto usa cache local (menos eficiente pero funcional)

### 4️⃣ **Configurar Variables de Entorno**

En Railway Dashboard → **Tu servicio → "Variables"**:

#### **Obligatorias:**

```env
# 1. SECRET_KEY (generar nueva)
SECRET_KEY=<tu-secret-key-aqui>

# 2. ALLOWED_HOSTS (tu dominio Railway)
ALLOWED_HOSTS=tu-app.up.railway.app
```

#### **Opcionales:**

```env
# Email (si quieres enviar emails)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# CORS (si tienes frontend separado)
CORS_ALLOWED_ORIGINS=https://tufrontend.com

# Sentry (monitoreo de errores)
SENTRY_DSN=https://...@sentry.io/...
```

---

## 🔑 Generar SECRET_KEY

### Opción 1: Management Command

```bash
# Localmente
python manage.py generate_secret_key

# En Railway
railway run python manage.py generate_secret_key
```

### Opción 2: Python One-liner

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Opción 3: OpenSSL

```bash
openssl rand -base64 50
```

---

## 📊 Resumen de Variables

| Variable | Requerida | Default | Quién la provee |
|----------|-----------|---------|-----------------|
| `SECRET_KEY` | ✅ Sí | ❌ Ninguno | **Tú (generar)** |
| `ALLOWED_HOSTS` | ✅ Sí | localhost | **Tú (tu dominio Railway)** |
| `DATABASE_URL` | ✅ Sí | ❌ Ninguno | **Railway (auto)** |
| `REDIS_URL` | ⚠️ Recomendado | LocMemCache | **Railway (auto)** |
| `EMAIL_HOST` | ❌ Opcional | Console | **Tú (SMTP)** |
| `SENTRY_DSN` | ❌ Opcional | Deshabilitado | **Tú (Sentry.io)** |

---

## ✅ Ventajas de Usar DATABASE_URL

### ❌ **Antes (5 variables)**
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=xxxxxxxxxxx
DB_HOST=containers-us-west-xxx.railway.app
DB_PORT=5432
```

### ✅ **Ahora (1 variable)**
```env
DATABASE_URL=postgresql://postgres:xxxxxxxxxxx@containers-us-west-xxx.railway.app:5432/railway
```

**Beneficios:**
- 🎯 **Más simple**: 1 variable en lugar de 5
- 🔧 **Railway-compatible**: Railway usa este formato estándar
- 🚀 **12-factor app**: Sigue las mejores prácticas
- 🔄 **Portabilidad**: Funciona en Heroku, Railway, Render, etc.

---

## 🔍 Verificar Configuración

### Durante Build (collectstatic)

```
✓ IS_BUILD_PHASE detected
✓ Using dummy SQLite database
✓ Using DummyCache
✓ collectstatic ejecutado sin errores
```

### Durante Runtime (servidor)

```
✓ IS_BUILD_PHASE = False
✓ DATABASE_URL parsed successfully
✓ PostgreSQL connected
✓ Redis connected (o LocMemCache si no está configurado)
✓ Server started on port $PORT
```

---

## 🐛 Troubleshooting

### Error: `DATABASE_URL not found`

**Causa:** No has agregado PostgreSQL en Railway

**Solución:**
```
Railway Dashboard → New → Database → PostgreSQL
```

### Error: `SECRET_KEY not found`

**Causa:** No configuraste SECRET_KEY

**Solución:**
```bash
# Generar uno
python manage.py generate_secret_key

# Agregarlo en Railway
Railway Dashboard → Variables → Add Variable
```

### Warning: `REDIS_URL not configured`

**Causa:** No has agregado Redis (no es crítico)

**Solución:** El proyecto funciona con cache local. Para mejor performance:
```
Railway Dashboard → New → Database → Redis
```

### Error: `ALLOWED_HOSTS must be set`

**Causa:** No configuraste tu dominio

**Solución:**
```env
# En Railway Variables
ALLOWED_HOSTS=tu-app.up.railway.app
```

---

## 📚 Documentación Relacionada

- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Guía completa de deployment
- **[SECURITY_NOTES.md](./majobacore/settings/SECURITY_NOTES.md)**: Estrategia de SECRET_KEY
- **[BUILD_PHASE_CHANGES.md](./BUILD_PHASE_CHANGES.md)**: Detección de build phase
- **[AGENTS.md](./AGENTS.md)**: Referencia técnica completa

---

## 🎉 Resultado Final

Con esta configuración simplificada:

- ✅ Build funciona sin configurar variables primero
- ✅ Solo 2 variables obligatorias inicialmente
- ✅ Railway provee DATABASE_URL automáticamente
- ✅ Deployment más rápido y simple
- ✅ Compatible con otros PaaS (Heroku, Render)

**¡Ya no necesitas 10+ variables de entorno para deployar!** 🚀
