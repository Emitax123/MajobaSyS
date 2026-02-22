# Variables de Entorno para Railway

Este documento lista las variables de entorno necesarias para desplegar MajobaSyS en Railway.

## Variables Obligatorias

### 1. SECRET_KEY (Crítico)
**Descripción:** Clave secreta de Django para criptografía y seguridad.

**Generar:**
```bash
python manage.py generate_secret_key
```

**Ejemplo:**
```
SECRET_KEY=h8oc=8$)z121ma74w%c)!*@vc=w5y8l(2lbj#0=l+jbn#jd%x@
```

### 2. DJANGO_SETTINGS_MODULE
**Descripción:** Módulo de configuración a usar.

**Valor:**
```
DJANGO_SETTINGS_MODULE=majobacore.settings.production
```

### 3. ALLOWED_HOSTS
**Descripción:** Dominios permitidos para servir la aplicación (separados por coma).

**Ejemplo:**
```
ALLOWED_HOSTS=tu-proyecto.up.railway.app,tudominio.com
```

### 4. DEBUG
**Descripción:** Modo debug (SIEMPRE False en producción).

**Valor:**
```
DEBUG=False
```

## Variables de Base de Datos (PostgreSQL)

Railway puede inyectar estas automáticamente si añades un servicio PostgreSQL:

```
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
```

## Variables de Cache (Redis)

Railway puede inyectar esta automáticamente si añades un servicio Redis:

```
REDIS_URL=${{Redis.REDIS_URL}}
```

## Variables de Email (Opcionales)

Para envío de correos y notificaciones de errores:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@tudominio.com
SERVER_EMAIL=admin@tudominio.com
ADMIN_EMAIL=tu-email@gmail.com
```

## Variables de Seguridad (Opcionales)

Estas tienen valores por defecto seguros, pero puedes personalizarlas:

```
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://tu-proyecto.up.railway.app
```

## Variables de AWS S3 (Opcional)

Solo si usas S3 para archivos media:

```
USE_S3=True
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_STORAGE_BUCKET_NAME=tu-bucket
AWS_S3_REGION_NAME=us-east-1
```

## Configuración Rápida en Railway

### Paso 1: Servicios Base
1. Crea tu proyecto en Railway
2. Añade servicio **PostgreSQL**
3. Añade servicio **Redis**
4. Conecta tu repositorio GitHub

### Paso 2: Variables de Entorno Mínimas
En la pestaña "Variables" de tu servicio web, añade:

```bash
SECRET_KEY=<tu-secret-key-generada>
DJANGO_SETTINGS_MODULE=majobacore.settings.production
DEBUG=False
ALLOWED_HOSTS=tu-proyecto.up.railway.app

# Referencias a servicios de Railway
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
REDIS_URL=${{Redis.REDIS_URL}}
```

### Paso 3: Deploy
Railway desplegará automáticamente. Los logs mostrarán el progreso.

## Notas Importantes

1. **BUILD vs RUNTIME:** El código ahora detecta automáticamente si está en fase de build (`collectstatic`) o runtime (servidor). Durante build, las variables de DB/Redis no son necesarias.

2. **SECRET_KEY:** Genera una nueva clave para cada entorno. NUNCA reutilices la del desarrollo.

3. **ALLOWED_HOSTS:** Actualiza este valor cada vez que cambies de dominio o añadas un dominio custom.

4. **Referencias de Railway:** Usa la sintaxis `${{Service.VARIABLE}}` para referenciar variables de otros servicios.

## Troubleshooting

### Error: "SECRET_KEY not found"
- Asegúrate de haber añadido la variable en Railway
- Verifica que no tenga espacios al inicio o final

### Error: "ALLOWED_HOSTS must be set"
- Añade tu dominio de Railway a ALLOWED_HOSTS
- El formato es: `proyecto.up.railway.app` (sin https://)

### Error: Database connection failed
- Verifica que el servicio PostgreSQL esté corriendo
- Comprueba que las referencias `${{Postgres.*}}` sean correctas
- Railway puede tardar unos segundos en iniciar la BD

### Error: Redis connection failed
- Verifica que el servicio Redis esté corriendo
- Railway proporciona `REDIS_URL` automáticamente
- Redis es opcional para collectstatic gracias a la detección de build phase
