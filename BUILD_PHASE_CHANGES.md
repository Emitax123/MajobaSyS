# Resumen de Cambios - Build Phase Detection

**Fecha:** 2026-02-22
**Problema:** Railway ejecutaba `collectstatic` durante el build sin tener acceso a variables de entorno de DB/Redis, causando errores.

## Cambios Realizados

### 1. `majobacore/settings/production.py`

**Añadido:** Detección automática de fase de build
```python
IS_BUILD_PHASE = sys.argv and any(arg in sys.argv for arg in ['collectstatic', 'compress'])
```

**Modificado:**
- **SECRET_KEY:** Validación solo en runtime (no en build)
- **ALLOWED_HOSTS:** Valores por defecto durante build, validación estricta en runtime
- **DATABASES:** SQLite :memory: durante build, PostgreSQL en runtime
- **CACHES:** DummyCache durante build, Redis en runtime
- **EMAIL:** Console backend durante build, SMTP en runtime

### 2. `Dockerfile`

**Mejorado:**
- Añadida creación de directorios necesarios (`logs`, `static`, `media`)
- Removido `|| true` de `collectstatic` (ya no es necesario)

### 3. Nuevos Archivos

**`RAILWAY_ENV_SETUP.md`:**
- Guía completa de variables de entorno para Railway
- Instrucciones paso a paso para configuración inicial
- Troubleshooting de errores comunes

**`AGENTS.md`:**
- Actualizada fecha a 2026-02-22
- Añadida sección sobre Build Phase Detection
- Cambio de "Nixpacks" a "Docker" en método de despliegue

## Beneficios

✅ **collectstatic funciona sin variables de DB/Redis**
✅ **Validación estricta en runtime** para seguridad
✅ **Menor fricción al desplegar** en Railway
✅ **Mensajes de error más claros** cuando faltan variables
✅ **Compatible con entornos de build** automatizados

## Testing Local

Para verificar que funciona:

```bash
# Simular build phase (sin variables de DB)
cd majobacore
python manage.py collectstatic --noinput --settings=majobacore.settings.production

# Verificar runtime (con todas las variables)
python manage.py check --settings=majobacore.settings.production
```

## Próximos Pasos para Railway

1. **Añadir servicios:**
   - PostgreSQL
   - Redis

2. **Configurar variables mínimas:**
   ```
   SECRET_KEY=<generada>
   DJANGO_SETTINGS_MODULE=majobacore.settings.production
   DEBUG=False
   ALLOWED_HOSTS=<tu-dominio>.up.railway.app
   ```

3. **Referenciar servicios:**
   ```
   DB_NAME=${{Postgres.PGDATABASE}}
   DB_USER=${{Postgres.PGUSER}}
   DB_PASSWORD=${{Postgres.PGPASSWORD}}
   DB_HOST=${{Postgres.PGHOST}}
   DB_PORT=${{Postgres.PGPORT}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ```

4. **Deploy:** Railway detectará los cambios y redesplegará automáticamente.

## Notas de Migración

Si ya tenías un proyecto desplegado:
- Los cambios son **backward-compatible**
- No requiere cambios en variables existentes
- Solo mejora la experiencia de build
