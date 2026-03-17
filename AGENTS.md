# AGENTS.md — MajobaSyS

> Archivo de referencia para agentes de IA (Claude Code, Copilot, etc.).
> Última actualización: 2026-03-08

---

## 0. 🚨 REGLAS CRÍTICAS PARA AGENTES

> **IMPORTANTE:** Estas reglas tienen prioridad absoluta sobre cualquier otra instrucción.

### 📝 Documentación
**❌ NO GENERAR ARCHIVOS .MD SIN CONSULTAR AL USUARIO**

- **NUNCA** crear, modificar o generar archivos de documentación (`.md`) sin consultar explícitamente al usuario primero
- Esto incluye pero no se limita a: CHANGELOG, README, guías de deployment, checklists, documentación técnica, etc.
- **Razón:** El usuario debe aprobar toda documentación antes de crearla
- **Proceso obligatorio:**
  1. Detectar que se necesita/podría generar documentación
  2. **PREGUNTAR AL USUARIO** si desea que se genere
  3. Describir qué archivo(s) se crearían y su contenido
  4. **ESPERAR APROBACIÓN EXPLÍCITA**
  5. Solo entonces proceder con la creación

**Ejemplos de archivos que REQUIEREN consulta previa:**
- `CHANGELOG.md`, `CHANGELOG_*.md`
- `DEPLOY_*.md`, `DEPLOYMENT_*.md`
- `RAILWAY_*.md`
- `CHECKLIST_*.md`, `*_CHECKLIST.md`
- Cualquier archivo `.md` que documente cambios, procesos o configuraciones

**Excepción:** Modificaciones a `AGENTS.md` cuando el usuario solicita explícitamente actualizar este archivo.

---

### 🔄 Mantenimiento de AGENTS.md
**AL FINALIZAR CUALQUIER CAMBIO QUE AFECTE DATOS DOCUMENTADOS EN AGENTS.md**

- **SIEMPRE** que se modifique algo que esté documentado en este archivo (modelos, URLs, dependencias, settings, estructura de archivos, comandos, roles/permisos, etc.), el agente **debe** proponer al usuario una actualización del apartado correspondiente
- **Proceso obligatorio:**
  1. Detectar qué secciones de `AGENTS.md` quedan desactualizadas tras los cambios realizados
  2. **PROPONER AL USUARIO** qué apartados necesitan actualización y describir los cambios
  3. **ESPERAR APROBACIÓN EXPLÍCITA**
  4. Solo entonces proceder con la actualización de `AGENTS.md`
- **Aplica a cambios en:** modelos de datos, URLs/rutas, dependencias, variables de entorno, estructura de directorios, comandos de desarrollo, configuración de entornos, roles/permisos, y cualquier otro dato referenciado en este archivo

---

## 1. Resumen del Proyecto

**MajobaSyS** (MajobaCore) es un sistema de gestión empresarial construido con **Django 5.2+** y desplegado en **Railway**. Permite administrar usuarios, proyectos y un sistema de puntos/niveles con notificaciones. La interfaz es server-side rendered con templates Django (no SPA).

- **Lenguaje:** Python 3.11
- **Framework:** Django 5.2+ (monolito con apps modulares)
- **Base de datos:** SQLite (dev) / PostgreSQL (producción)
- **Cache:** DummyCache (dev) / Redis (producción)
- **Servidor:** Gunicorn (producción)
- **Despliegue:** Railway (Nixpacks)
- **Idioma principal del código:** Español (labels, verbose_names, mensajes de usuario)

### Build Phase Detection (Importante)

**Desde 2026-02-22**, `base.py` y `production.py` detectan automáticamente si están en fase de **BUILD** (`collectstatic`) o **RUNTIME** (servidor):

- **BUILD Phase:** Usa configuraciones dummy (SQLite :memory:, DummyCache, console email)
- **RUNTIME Phase:** Valida estrictamente todas las variables de entorno (PostgreSQL, Redis, SMTP)

Esta distinción permite que `collectstatic` funcione sin necesidad de variables de DB/Redis, resolviendo conflictos de despliegue en Railway.

**Variables requeridas SOLO en RUNTIME:**
- `DATABASE_URL` — Railway lo provee automáticamente al añadir PostgreSQL (formato: `postgresql://user:password@host:port/dbname`). Parseada con `dj-database-url`.
- `REDIS_URL`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (si se usa email)

**Variables requeridas SIEMPRE:**
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DJANGO_SETTINGS_MODULE`

**Variables opcionales:**
- `ADMIN_URL` — Cambia la URL del panel de administración (default: `admin/`). Se recomienda una URL no predecible en producción.
- `SENTRY_DSN` — Activa monitoreo de errores con Sentry si se configura.
- `CORS_ALLOWED_ORIGINS` — Activa `django-cors-headers` si se configura.
- `USE_S3` — Activa almacenamiento S3 para archivos media si es `True`.

---

## 2. Estructura del Proyecto

```
MajobaSyS/                         ← Raíz del repositorio y proyecto Django
├── manage.py                      ← Script de gestión Django
├── db.sqlite3                     ← BD local de desarrollo
├── Procfile                       ← Comando de arranque para Railway (migrate + ensure_superuser + gunicorn)
├── railway.toml                   ← Config de despliegue Railway (builder, build command, healthcheck)
├── requirements.txt               ← Wrapper que apunta a requirements/production.txt (usado por Railway/Nixpacks)
├── runtime.txt                    ← Versión de Python para Railway: python-3.11
├── pytest.ini                     ← Config de pytest + coverage
├── run_dev.bat                    ← Script rápido para correr en Windows
├── setup_dev.bat                  ← Script de setup inicial en Windows
├── test_healthcheck.py            ← Script manual para verificar los endpoints de health check
├── README.md                      ← README principal del proyecto
├── .gitignore                     ← Archivos ignorados por Git
├── .dockerignore                  ← Archivos ignorados por Docker
├── .editorconfig                  ← Configuración de estilo de editor
├── .env                           ← Variables de entorno locales (no commiteado)
├── .env.example                   ← Plantilla de variables de entorno
├── .env.test                      ← Variables de entorno para tests
├── AGENTS.md                      ← Este archivo
├── requirements/
│   ├── base.txt                   ← Deps compartidas (Django, Celery, Redis, Pillow, dj-database-url, etc.)
│   ├── development.txt            ← Deps dev (debug-toolbar, pytest, black, flake8, etc.)
│   └── production.txt             ← Deps prod (sentry-sdk, boto3, django-cors-headers, etc.)
│
├── majobacore/                    ← Paquete principal del proyecto Django
│   ├── __init__.py
│   ├── urls.py                    ← URL raíz: admin (configurable), manager/, users/, páginas estáticas, health checks
│   ├── views.py                   ← Vistas: páginas estáticas, coming_soon, health_check, liveness_check, readiness_check, budget (con envío de email)
│   ├── wsgi.py
│   ├── asgi.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                ← Settings comunes (AUTH_USER_MODEL, logging, cache, CSRF, sesiones, ADMIN_URL)
│   │   ├── development.py         ← SQLite, DEBUG=True, debug-toolbar, DummyCache
│   │   ├── production.py          ← PostgreSQL (DATABASE_URL), SSL, HSTS, Redis, Sentry, JSON logging
│   │   └── testing.py             ← SQLite :memory:, MD5 hasher, Celery eager, sin migraciones
│   ├── utils/
│   │   └── security.py            ← SecurityHeadersMiddleware, rate limit config, helpers
│   └── management/
│       └── commands/
│           ├── generate_secret_key.py
│           └── check_production_settings.py
│
├── users/                         ← App de autenticación y usuarios
│   ├── models.py                  ← CustomUser (extiende AbstractUser)
│   ├── views.py                   ← Login, logout, registro, perfil, modificación de usuarios
│   ├── forms.py                   ← CustomUserCreationForm, CustomUserChangeForm, CustomLoginForm
│   ├── urls.py                    ← create/, login/, logout/, profile/, modify/<id>/
│   ├── admin.py                   ← CustomUserAdmin con fieldsets personalizados
│   └── tests.py
│
├── manager/                       ← App de gestión (clientes, proyectos, puntos, notificaciones)
│   ├── models.py                  ← Client, Project, Notification, ManagerData
│   ├── views.py                   ← Dashboard, CRUD proyectos, modificación de manager, búsqueda AJAX
│   ├── forms.py                   ← ClientForm, ManagerDataForm, ProjectForm
│   ├── urls.py                    ← Manager dashboard, admin-dashboard, proyectos, búsqueda
│   ├── admin.py                   ← Registro de Client, ManagerData, Project, Notification
│   ├── tests.py
│   └── management/
│       └── commands/
│           └── ensure_superuser.py ← Crea superusuario desde variables de entorno en cada deploy
│
├── templates/                     ← Templates Django
│   ├── base.html                  ← Layout base
│   ├── index.html                 ← Landing page
│   ├── carousel.html
│   ├── budget_form.html           ← Formulario de presupuesto (GET + POST con envío de email)
│   ├── coming_soon.html           ← Página "en construcción" para /herramientas/
│   ├── majoba_template.html
│   ├── hormicons_template.html
│   ├── constructora_template.html
│   ├── 400.html                   ← Error handler personalizado
│   ├── 403.html                   ← Error handler personalizado
│   ├── 404.html                   ← Error handler personalizado
│   ├── 500.html                   ← Error handler personalizado
│   ├── manager/                   ← Templates de la app manager
│   │   ├── account_manager.html
│   │   ├── admin_dashboard.html
│   │   ├── create_project.html
│   │   ├── modify_manager.html
│   │   ├── modify_project.html
│   │   ├── projects_list.html
│   │   ├── staff_template.html
│   │   └── manage_acc_create.html
│   └── users/                     ← Templates de la app users
│       ├── login.html
│       ├── user_create.html
│       └── user_modify.html
│
├── static/                        ← Archivos estáticos
│   ├── css/                       ← admin_dashboard.css, base.css, budget_form.css, carousel.css,
│   │                                 carousel-fallback.css, create_user.css, index.css, login.css,
│   │                                 modify_manager.css, modify_manager_new.css
│   ├── js/                        ← base.js, admin-dashboard.js, search.js, manager.js
│   └── images/                    ← majoba/, hormicons/, constructora/, favicon_io/, brandlogos/,
│                                     más imágenes sueltas (banners, sliders, SVGs, logos de tarjeta)
│
├── media/                         ← Archivos subidos por usuarios
└── logs/                          ← Directorio de logs (Railway captura stdout; solo se usa localmente)
```

---

## 3. Modelos de Datos

### `manager.Client`
| Campo      | Tipo                    | Notas                              |
|------------|-------------------------|------------------------------------|
| user       | ForeignKey(CustomUser)  | `related_name='clients'`           |
| name       | CharField(255)          | Requerido                          |
| phone      | CharField(20)           | Requerido                          |
| created_at | DateTimeField           | Auto                               |

- Ordering: `['name']`
- Cada usuario tiene sus propios clientes. Un cliente puede asociarse a múltiples proyectos.

### `users.CustomUser` (extiende `AbstractUser`)
| Campo      | Tipo           | Notas                                     |
|------------|----------------|-------------------------------------------|
| username   | CharField      | Campo principal de login (USERNAME_FIELD) |
| email      | EmailField     | Opcional (blank=True, null=True)          |
| first_name | CharField(150) | Requerido                                 |
| last_name  | CharField(150) | Requerido                                 |
| phone      | CharField(20)  | Requerido                                 |
| profession | CharField(100) | Opcional                                  |
| direction  | CharField(255) | Opcional (dirección/ubicación)            |
| is_active  | BooleanField   | Default True                              |
| is_staff   | BooleanField   | Indica si es administrador                |
| created_at | DateTimeField  | Auto                                      |
| updated_at | DateTimeField  | Auto                                      |

- `AUTH_USER_MODEL = 'users.CustomUser'`
- `REQUIRED_FIELDS = []` — Sin campos extra requeridos aparte de username/password
- Al crear un usuario se crea automáticamente un `ManagerData` asociado

### `manager.ManagerData` (Perfil/Gamificación)
| Campo         | Tipo                      | Notas                                                      |
|---------------|---------------------------|------------------------------------------------------------|
| user          | OneToOneField(CustomUser) | `related_name='manager_user'`                              |
| points        | IntegerField              | Default 0                                                  |
| acc_level     | CharField(20)             | Choices: principiante/intermedio/avanzado/experto/maestro  |
| notifications | IntegerField              | Contador de notificaciones                                 |
| created_at    | DateTimeField             | Auto                                                       |
| updated_at    | DateTimeField             | Auto                                                       |

**Sistema de niveles por puntos:**
- Principiante: 0–499
- Intermedio: 500–1999
- Avanzado: 2000–4999
- Experto: 5000–9999
- Maestro: 10000+

**Métodos y propiedades clave:**
- `add_points()`, `spend_points()`, `update_level()` — métodos regulares
- `progress_percentage` — `@property` — porcentaje de progreso dentro del nivel actual (0–100)
- `points_for_next_level` — `@property` — puntos que faltan para el siguiente nivel
- `next_level_display` — `@property` — nombre legible del siguiente nivel
- `_nivel_canonico()` — método interno que recalcula el nivel desde puntos si `acc_level` tiene un valor corrupto/inválido

### `manager.Project`
| Campo       | Tipo                   | Notas                                         |
|-------------|------------------------|-----------------------------------------------|
| user        | ForeignKey(CustomUser) | `related_name='projects'`                     |
| client      | ForeignKey(Client)     | `related_name='projects'`, null=True, PROTECT |
| name        | CharField(255)         | Requerido                                     |
| description | TextField              | Opcional                                      |
| location    | CharField(255)         | Opcional                                      |
| start_date  | DateField              | Requerido                                     |
| end_date    | DateField              | Opcional                                      |
| is_active   | BooleanField           | Default True                                  |
| created_at  | DateTimeField          | Auto                                          |
| updated_at  | DateTimeField          | Auto                                          |

### `manager.Notification`
| Campo       | Tipo                   | Notas                              |
|-------------|------------------------|------------------------------------|
| user        | ForeignKey(CustomUser) | `related_name='notifications'`     |
| message     | CharField(255)         | Mensaje corto                      |
| description | TextField              | Descripción detallada (opcional)   |
| is_read     | BooleanField           | Default False                      |
| created_at  | DateTimeField          | Auto                               |

**Métodos:**
- `time_elapsed()` — devuelve tiempo transcurrido en español legible (ej: "hace 5 minutos", "hace 2 días")

---

## 4. URLs y Rutas

### Raíz (`majobacore/urls.py`)
| Ruta                  | Vista/Include             | Name            | Notas                              |
|-----------------------|---------------------------|-----------------|------------------------------------|
| `<ADMIN_URL>`         | admin.site.urls           | —               | Configurable via env (default: `admin/`) |
| `/manager/`           | include('manager.urls')   | —               |                                    |
| `/users/`             | include('users.urls')     | —               |                                    |
| `/`                   | index                     | `index`         |                                    |
| `/majoba/`            | majoba_view               | `majoba`        |                                    |
| `/hormicons/`         | hormicons_view            | `hormicons`     |                                    |
| `/constructora/`      | constructora_view         | `constructora`  |                                    |
| `/budget/`            | budget_view               | `budget`        | GET + POST (envío de email)        |
| `/herramientas/`      | coming_soon_view          | `herramientas`  | Página "en construcción"           |
| `/health/`            | health_check              | `health_check`  | JSON: DB + cache status            |
| `/health/live/`       | liveness_check            | `liveness`      | Liveness probe (texto plano "OK")  |
| `/health/ready/`      | readiness_check           | `readiness`     | Readiness probe (verifica DB)      |
| `/__debug__/`         | debug_toolbar             | —               | Solo cuando `DEBUG=True`           |

**Error handlers personalizados** (activos cuando `DEBUG=False`):
- `handler400`, `handler403`, `handler404`, `handler500` — usan templates `400.html`, `403.html`, `404.html`, `500.html`

### Users (`users/urls.py`)
| Ruta                       | Vista              | Name          |
|----------------------------|--------------------|---------------|
| `/users/create/`           | user_create_view   | `user_create` |
| `/users/login/`            | custom_login_view  | `login`       |
| `/users/logout/`           | custom_logout_view | `logout`      |
| `/users/profile/`          | profile_view       | `profile`     |
| `/users/modify/<user_id>/` | user_modification  | `user_modify` |

### Manager (`manager/urls.py`)
| Ruta                                    | Vista                | Name                   |
|-----------------------------------------|----------------------|------------------------|
| `/manager/`                             | manager_view         | `manager`              |
| `/manager/admin-dashboard/`             | admin_dashboard_view | `admin_dashboard`      |
| `/manager/list-projects/`               | list_projects_view   | `list_projects`        |
| `/manager/modify-project/<project_id>/` | modify_project_view  | `modify_project`       |
| `/manager/modify/<user_id>/`            | manager_modification | `manager_modification` |
| `/manager/search/`                      | search_users_ajax    | `search`               |
| `/manager/create-project/`              | create_project_view  | `create_project`       |

---

## 5. Roles y Permisos

| Rol                               | Accesos                                                                                         |
|-----------------------------------|-------------------------------------------------------------------------------------------------|
| **Staff/Admin** (`is_staff=True`) | Admin dashboard, crear usuarios, modificar ManagerData, búsqueda AJAX, CRUD proyectos, Django Admin |
| **Usuario normal** (`is_staff=False`) | Manager dashboard (su cuenta), ver/crear/editar sus proyectos, ver notificaciones, perfil    |

- Login redirige según `is_staff`: staff → `admin_dashboard`, usuario normal → `manager`
- Al crear un usuario se crea automáticamente un `ManagerData` con `create_manager()`
- El admin dashboard requiere `@login_required` + verificación `is_staff`

---

## 6. Entornos y Settings

| Entorno        | Settings Module                    | BD               | Cache      | Debug |
|----------------|------------------------------------|------------------|------------|-------|
| **Desarrollo** | `majobacore.settings.development`  | SQLite           | DummyCache | True  |
| **Producción** | `majobacore.settings.production`   | PostgreSQL       | Redis      | False |
| **Testing**    | `majobacore.settings.testing`      | SQLite :memory:  | DummyCache | False |

**Variable de entorno clave:** `DJANGO_SETTINGS_MODULE`

### Variables de Entorno (.env)
```
SECRET_KEY=...
DEBUG=True/False
DJANGO_SETTINGS_MODULE=majobacore.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (producción: una sola variable)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Base de datos (desarrollo: variables individuales, base.py las lee)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Cache
REDIS_URL=redis://127.0.0.1:6379/1

# Email
EMAIL_HOST=...
EMAIL_PORT=465
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...

# Seguridad
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Opcionales
ADMIN_URL=admin/
SENTRY_DSN=...
CORS_ALLOWED_ORIGINS=https://example.com
USE_S3=False
```

---

## 7. Comandos de Desarrollo

```bash
# Desde la raíz del repositorio (donde está manage.py)

# Instalar dependencias
pip install -r requirements/development.txt

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
# O usar: run_dev.bat

# Generar secret key
python manage.py generate_secret_key

# Coleccionar estáticos
python manage.py collectstatic --noinput

# Tests
pytest                              # Todos los tests
pytest users/                       # Tests de users
pytest manager/                     # Tests de manager
pytest -m unit                      # Solo tests unitarios
pytest -m integration               # Solo tests de integración
pytest --cov                        # Con coverage

# Formateo y linting
black .
isort .
flake8
```

---

## 8. Testing

- **Framework:** pytest + pytest-django
- **Config:** `pytest.ini` en la raíz del proyecto Django
- **Settings:** `majobacore.settings.testing` (SQLite :memory:, MD5 hasher para velocidad)
- **Coverage:** Se mide sobre `users/` y `manager/`, excluyendo migraciones
- **Markers:** `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit`
- **Flags activos:** `--reuse-db`, `--nomigrations`, `--strict-markers`, `--disable-warnings`
- **Celery en tests:** `CELERY_TASK_ALWAYS_EAGER = True` (ejecución síncrona)

---

## 9. Despliegue (Railway)

- **Builder:** Nixpacks (maneja `pip install` automáticamente desde `requirements.txt`)
- **Build command:** `python manage.py collectstatic --noinput --settings=majobacore.settings.production`
- **No hay release phase separado** — migrate se ejecuta inline al inicio del proceso web
- **Start (Procfile):**
  ```
  web: python manage.py migrate --settings=majobacore.settings.production --noinput \
       && python manage.py ensure_superuser --settings=majobacore.settings.production \
       && gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 \
          --timeout 120 --access-logfile - --error-logfile -
  ```
- **Healthcheck:** `/health/live/` con timeout de 100s
- **Restart policy:** `ON_FAILURE`, max 10 retries
- **Estáticos:** WhiteNoise (`CompressedManifestStaticFilesStorage`)
- **Config file:** `railway.toml` (ya no existe `railway.json`)

---

## 10. Dependencias Principales

| Paquete                | Uso                                                         |
|------------------------|-------------------------------------------------------------|
| Django 5.2+            | Framework web                                               |
| python-decouple        | Gestión de variables de entorno (.env)                      |
| dj-database-url        | Parseo de `DATABASE_URL` para configurar PostgreSQL         |
| Pillow                 | Procesamiento de imágenes                                   |
| whitenoise             | Servir estáticos en producción                              |
| django-extensions      | Utilidades extra para Django                                |
| celery + redis         | Tareas asíncronas (configurado, sin tareas definidas aún)   |
| django-redis           | Backend de cache Redis para Django                          |
| gunicorn               | Servidor WSGI de producción                                 |
| psycopg2-binary        | Driver PostgreSQL                                           |
| requests               | Cliente HTTP (dependencia base)                             |
| python-json-logger     | Logging estructurado en formato JSON (producción)           |
| django-debug-toolbar   | Debug en desarrollo                                         |
| pytest + pytest-django | Testing                                                     |
| black + isort + flake8 | Formateo y linting                                          |
| sentry-sdk             | Monitoreo de errores (producción, activado con `SENTRY_DSN`)|
| boto3 + django-storages| Almacenamiento S3 (activado con `USE_S3=True`)              |
| django-cors-headers    | CORS (activado con `CORS_ALLOWED_ORIGINS`)                  |

---

## 11. Logging

- **Handlers activos:** `console` (stdout, nivel INFO) + `mail_admins` (ERROR, solo en producción con `DEBUG=False`)
- **No hay file handlers** — no se escriben logs a disco. En Railway, stdout es capturado automáticamente.
- **Loggers configurados:** `django`, `django.request`, `django.security`, `django.db.backends`, `majobacore`, `users`, `manager`
- **Producción:** El handler `console` usa formato JSON estructurado via `python-json-logger`, lo que facilita búsqueda en los logs de Railway.
- **Testing:** El logging se reduce a nivel WARNING para no ensuciar el output de pytest.

---

## 12. Seguridad

- **Producción:** HTTPS redirect, HSTS (1 año con subdomains + preload), cookies seguras, X-Frame-Options DENY
- **`SECURE_REDIRECT_EXEMPT`:** Los paths `/health/*` están exentos del redirect HTTPS (Railway los llama internamente por HTTP)
- **SecurityHeadersMiddleware** en `majobacore/utils/security.py`: añade headers X-Content-Type-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy (solo activo en producción)
- **CSRF:** cookie HttpOnly, SameSite=Lax, orígenes confiados configurables. Dominio Railway se añade automáticamente si `RAILWAY_PUBLIC_DOMAIN` está definido.
- **Sesiones:** backend cache (Redis en prod, cache default en dev), 24h en dev / 1h en prod, HttpOnly
- **Passwords:** `UserAttributeSimilarityValidator`, `MinimumLengthValidator` (**12 caracteres**), `CommonPasswordValidator`, `NumericPasswordValidator`
- **ADMIN_URL:** configurable via variable de entorno. Se recomienda una URL no predecible en producción (ej: `secretpanel/`). Default: `admin/`.
- **Rate limiting:** configurado en `security.py` (5/min login, 3/min registro, 1000/h API)

---

## 13. Convenciones de Código

- **Idioma del código:** Los nombres de variables, funciones y clases están en **inglés**; la documentación, labels de modelos, mensajes al usuario y verbose_names están en **español**
- **Vistas:** Todas basadas en funciones (FBV), no se usan Class-Based Views
- **Decoradores:** `@login_required` para vistas protegidas, verificación manual de `is_staff` para admin
- **Formularios:** Usan `ModelForm` con widgets personalizados y clases CSS Bootstrap-like
- **Logging:** Cada app tiene su propio logger (`logging.getLogger('app_name')`)
- **Transacciones:** `@transaction.atomic` en operaciones críticas de puntos
- **Operaciones atómicas:** Uso de `F()` expressions para actualización de puntos (prevent race conditions)
- **Templates:** Herencia con `base.html`, archivos estáticos servidos con `{% static %}`
- **Archivos estáticos:** CSS/JS organizados por funcionalidad en `static/css/` y `static/js/`
- **Migraciones:** Se generan por app, nombradas secuencialmente
- **QuerySets optimizados:** Usar `select_related()` para FK y `only()` para cargar solo los campos necesarios (ver `list_projects_view`)

---

## 14. Patrones Importantes

### Creación de usuario con perfil
Cuando se crea un `CustomUser`, se invoca `create_manager(user)` para generar automáticamente el `ManagerData` asociado. Esto ocurre tanto en el registro como en el login (si no existe).

### Sistema de puntos
Los puntos se modifican con `F()` expressions para operaciones atómicas. Al restar puntos, se usa `models.Case`/`models.When` para prevenir valores negativos. Las notificaciones se crean opcionalmente al modificar puntos.

### Creación inline de clientes
`create_project_view` soporta crear un `Client` al vuelo: si el POST incluye `new_client_name` (no vacío), se crea un nuevo cliente y se asigna al proyecto, ignorando el campo `client` del formulario. La lógica de validación está en `ProjectForm.clean()`.

### Filtro de proyectos por cliente
`list_projects_view` acepta el parámetro GET `?client=<id>` para filtrar proyectos por cliente. Usa `select_related('client')` y `only(...)` para optimizar la query (no carga campos no usados en la vista, como `description`).

### Búsqueda AJAX
`search_users_ajax` devuelve JSON paginado. Solo accesible por staff. Filtra por username, first_name, last_name con `icontains`.

### Redirección post-login
Staff → `admin_dashboard` | Usuario normal → `manager`

### ensure_superuser en deploy
El comando `manager/management/commands/ensure_superuser.py` se ejecuta en cada deploy (antes de gunicorn) para garantizar que existe un superusuario. Lee credenciales desde variables de entorno. Es idempotente — no falla si el usuario ya existe.

### Health checks
Tres endpoints diferenciados para Railway:
- `/health/` — Completo: verifica DB + cache, devuelve JSON con status detallado
- `/health/live/` — Liveness: ultra-ligero, solo confirma que la app responde ("OK")
- `/health/ready/` — Readiness: verifica conexión a BD antes de aceptar tráfico

---

## 15. Notas para Agentes

1. **🚨 CONSULTAR ANTES DE DOCUMENTAR:** NUNCA generar archivos .md sin aprobación explícita del usuario (ver sección 0)
2. **Directorio de trabajo:** Los comandos Django se ejecutan desde la raíz del repositorio (donde está `manage.py`)
3. **Estructura reorganizada (2026-02-22):** El proyecto fue reorganizado para Railway. Todos los archivos Django están ahora en la raíz del repositorio en lugar de dentro de una subcarpeta `majobacore/`
4. **No hay API REST formal:** Las vistas son server-side rendered con dos excepciones AJAX: `search_users_ajax` y los endpoints de health check (JSON)
5. **Celery configurado pero sin tareas:** Las dependencias están instaladas y el testing lo soporta (`ALWAYS_EAGER`), pero no hay tareas Celery definidas aún
6. **Sistema operativo del desarrollador:** Windows
7. **Sin Docker local:** El proyecto no usa Docker para desarrollo; se ejecuta directamente con venv en Windows. Railway usa Nixpacks.
8. **STATICFILES_DIRS** apunta a `static/` en la raíz del proyecto
9. **Logs:** El directorio `logs/` existe en raíz pero los settings no escriben a disco. Railway captura stdout automáticamente.
10. **El admin de Django** está en la URL configurada por `ADMIN_URL` (default `admin/`) y es funcional con `CustomUserAdmin` personalizado
11. **Bootstrap-like CSS:** Los formularios usan clases como `form-control`; no hay framework CSS formal instalado, los estilos son custom
12. **Al modificar modelos:** siempre ejecutar `makemigrations` y `migrate`; las migraciones existentes están en cada app
13. **Railway deployment:** Config en `railway.toml`. El `requirements.txt` de la raíz apunta a `requirements/production.txt` y es el que usa Nixpacks.
14. **`manager.Client` es un modelo propio del usuario:** cada usuario gestiona su propia lista de clientes. Un proyecto siempre tiene un cliente asociado (requerido por `ProjectForm.clean()`).
