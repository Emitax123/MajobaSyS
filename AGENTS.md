# AGENTS.md — MajobaSyS

> Última actualización: 2026-03-17

---

## 0. Reglas Críticas

**NUNCA generar archivos .md sin consultar al usuario primero** (CHANGELOG, README, guías, etc.)

Al finalizar cambios que afecten datos documentados aquí, **proponer** actualización.

---

## 1. Proyecto

- **Stack:** Django 5.2+, Python 3.11, PostgreSQL (prod), SQLite (dev), Redis (prod cache)
- **Despliegue:** Railway (Nixpacks)
- **API:** DRF + SimpleJWT en `/api/v1/` (JWT stateless)

### Vars requeridas en RUNTIME
- `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`

### Vars opcionales
- `ADMIN_URL` (default: `admin/`), `SENTRY_DSN`, `CORS_ALLOWED_ORIGINS`, `USE_S3`

---

## 2. Modelos

| Modelo | Campos clave |
|--------|-------------|
| `CustomUser` | username, email, first_name, last_name, phone, is_staff |
| `ManagerData` | user (OneToOne), points (int), acc_level (principiante→maestro), notifications |
| `Client` | user, name, phone |
| `Project` | user, client (FK), name, start_date, end_date, is_active |
| `Notification` | user, message, is_read, created_at |

### Sistema de niveles
- Principiante: 0-499 | Intermedio: 500-1999 | Avanzado: 2000-4999 | Experto: 5000-9999 | Maestro: 10000+

---

## 3. URLs Principales

| Ruta | Vista |
|------|-------|
| `/` | Landing page |
| `/manager/` | Dashboard usuario |
| `/manager/admin-dashboard/` | Dashboard admin (is_staff) |
| `/users/login/` | Login |
| `/health/` | Health check JSON |
| `/api/v1/auth/` | Auth JWT |
| `/api/v1/projects/` | Projects CRUD |
| `/api/v1/clients/` | Clients CRUD |
| `/api/v1/notifications/` | Notifications CRUD |

---

## 4. Permisos

- **Staff:** Admin dashboard, CRUD usuarios/proyectos, búsqueda AJAX, Django Admin
- **Usuario:** Su dashboard, proyectos propios, notificaciones, perfil

---

## 5. Comandos

```bash
# Desarrollo
pip install -r requirements/development.txt
python manage.py migrate
python manage.py runserver

# Deploy
python manage.py collectstatic --noinput
pytest

# Format
black . && isort .
```

---

## 6. Entornos

| Entorno | Settings | BD | Debug |
|---------|----------|-----|-------|
| Dev | `development` | SQLite | True |
| Prod | `production` | PostgreSQL | False |
| Test | `testing` | SQLite :memory: | False |

---

## 7. Patrones Clave

- Crear usuario → `create_manager(user)` (genera ManagerData automático)
- Puntos → usar `F()` expressions para atomicidad
- Login → staff→admin_dashboard, usuario→manager
- Health: `/health/` (full), `/health/live/` (liveness), `/health/ready/` (readiness)

---

## 8. Notas

1. Consultar antes de documentar
2. Django commands desde raíz (donde manage.py)
3. OS: Windows | Railway: Nixpacks
4. Al modificar modelos: makemigrations + migrate
5. API REST usa JWT Bearer tokens
6. ADMIN_URL configurable (recomendado no predecible en prod)

---

## 9. Agentes Disponibles

| Agente | Uso |
|--------|-----|
| `frontend-developer` | UI/UX, HTML, CSS, JS en templates Django |
| `majobasys-master-agent` | Tareas full stack completas |

### Flujo de Trabajo
- **Frontend puro** → `frontend-developer`
- **Tareas mixtas/completas** → `majobasys-master-agent`
- **Investigación** → usar agente `explore`
- **Debugging** → cargar `systematic-debugging` skill antes de proponer fixes
