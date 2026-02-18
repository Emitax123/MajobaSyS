# AGENTS.md — MajobaSyS

> Archivo de referencia para agentes de IA (Claude Code, Copilot, etc.).
> Última actualización: 2026-02-18

---

## 1. Resumen del Proyecto

**MajobaSyS** (MajobaCore) es un sistema de gestión empresarial construido con **Django 5.2+** y desplegado en **Railway**. Permite administrar usuarios, proyectos y un sistema de puntos/niveles con notificaciones. La interfaz es server-side rendered con templates Django (no SPA).

- **Lenguaje:** Python 3.x
- **Framework:** Django 5.2+ (monolito con apps modulares)
- **Base de datos:** SQLite (dev) / PostgreSQL (producción)
- **Cache:** DummyCache (dev) / Redis (producción)
- **Servidor:** Gunicorn (producción)
- **Despliegue:** Railway (Nixpacks)
- **Idioma principal del código:** Español (labels, verbose_names, mensajes de usuario)

---

## 2. Estructura del Proyecto

```
MajobaSyS/                         ← Raíz del repositorio
└── majobacore/                     ← Directorio del proyecto Django (manage.py vive aquí)
    ├── manage.py
    ├── db.sqlite3                  ← BD local de desarrollo
    ├── Procfile                    ← Comandos Railway (migrate + gunicorn)
    ├── railway.json                ← Config de despliegue Railway
    ├── pytest.ini                  ← Config de pytest + coverage
    ├── run_dev.bat                 ← Script rápido para correr en Windows
    ├── setup_dev.bat               ← Script de setup inicial en Windows
    ├── requirements/
    │   ├── base.txt                ← Deps compartidas (Django, Celery, Redis, Pillow, etc.)
    │   ├── development.txt         ← Deps dev (debug-toolbar, pytest, black, flake8, etc.)
    │   └── production.txt          ← Deps prod (sentry-sdk, boto3, newrelic, etc.)
    │
    ├── majobacore/                 ← Paquete principal del proyecto Django
    │   ├── __init__.py
    │   ├── urls.py                 ← URL raíz: admin/, manager/, users/, páginas estáticas
    │   ├── views.py                ← Vistas de páginas estáticas (index, majoba, hormicons, constructora, budget)
    │   ├── wsgi.py
    │   ├── asgi.py
    │   ├── settings/
    │   │   ├── __init__.py
    │   │   ├── base.py             ← Settings comunes (AUTH_USER_MODEL, logging, cache, CSRF, sesiones)
    │   │   ├── development.py      ← SQLite, DEBUG=True, debug-toolbar, DummyCache
    │   │   ├── production.py       ← PostgreSQL, SSL, HSTS, Redis, Sentry-ready
    │   │   └── testing.py          ← SQLite :memory:, MD5 hasher, Celery eager, sin migraciones
    │   ├── utils/
    │   │   └── security.py         ← SecurityHeadersMiddleware, rate limit config, helpers
    │   └── management/
    │       └── commands/
    │           └── generate_secret_key.py
    │
    ├── users/                      ← App de autenticación y usuarios
    │   ├── models.py               ← CustomUser (extiende AbstractUser)
    │   ├── views.py                ← Login, logout, registro, perfil, modificación de usuarios
    │   ├── forms.py                ← CustomUserCreationForm, CustomUserChangeForm, CustomLoginForm
    │   ├── urls.py                 ← create/, login/, logout/, profile/, modify/<id>/
    │   ├── admin.py                ← CustomUserAdmin con fieldsets personalizados
    │   └── tests.py
    │
    ├── manager/                    ← App de gestión (proyectos, puntos, notificaciones)
    │   ├── models.py               ← Project, Notification, ManagerData
    │   ├── views.py                ← Dashboard, CRUD proyectos, modificación de manager, búsqueda AJAX
    │   ├── forms.py                ← ManagerDataForm, ProjectForm
    │   ├── urls.py                 ← Manager dashboard, admin-dashboard, proyectos, búsqueda
    │   ├── admin.py                ← Registro básico de modelos
    │   └── tests.py
    │
    ├── templates/                  ← Templates Django (Jinja-like)
    │   ├── base.html               ← Layout base
    │   ├── index.html              ← Landing page
    │   ├── carousel.html
    │   ├── budget_form.html
    │   ├── majoba_template.html
    │   ├── hormicons_template.html
    │   ├── constructora_template.html
    │   ├── manager/                ← Templates de la app manager
    │   │   ├── account_manager.html
    │   │   ├── admin_dashboard.html
    │   │   ├── create_project.html
    │   │   ├── modify_manager.html
    │   │   ├── modify_project.html
    │   │   ├── projects_list.html
    │   │   ├── staff_template.html
    │   │   └── manage_acc_create.html
    │   └── users/                  ← Templates de la app users
    │       ├── login.html
    │       ├── user_create.html
    │       └── user_modify.html
    │
    ├── static/                     ← Archivos estáticos
    │   ├── css/                    ← Estilos (base.css, admin_dashboard.css, etc.)
    │   ├── js/                     ← JavaScript (base.js, admin-dashboard.js, search.js, manager.js)
    │   └── images/                 ← Imágenes y logos (majoba/, hormicons/, constructora/, favicon_io/)
    │
    ├── media/                      ← Archivos subidos por usuarios
    └── logs/                       ← Archivos de log (info.log, errors.log)
```

---

## 3. Modelos de Datos

### `users.CustomUser` (extiende `AbstractUser`)
| Campo        | Tipo                | Notas                                  |
|------------- |---------------------|----------------------------------------|
| username     | CharField           | Campo principal de login (USERNAME_FIELD) |
| email        | EmailField          | Opcional (blank=True, null=True)       |
| first_name   | CharField(150)      | Requerido                              |
| last_name    | CharField(150)      | Requerido                              |
| phone        | CharField(20)       | Requerido                              |
| profession   | CharField(100)      | Opcional                               |
| direction    | CharField(255)      | Opcional (dirección/ubicación)         |
| is_active    | BooleanField        | Default True                           |
| is_staff     | BooleanField        | Indica si es administrador             |
| created_at   | DateTimeField       | Auto                                   |
| updated_at   | DateTimeField       | Auto                                   |

- `AUTH_USER_MODEL = 'users.CustomUser'`
- `REQUIRED_FIELDS = []` — Sin campos extra requeridos aparte de username/password
- Al crear un usuario se crea automáticamente un `ManagerData` asociado

### `manager.ManagerData` (Perfil/Gamificación)
| Campo         | Tipo              | Notas                                         |
|-------------- |-------------------|-----------------------------------------------|
| user          | OneToOneField(CustomUser) | `related_name='manager_user'`          |
| points        | IntegerField      | Default 0                                     |
| acc_level     | CharField(20)     | Choices: principiante/intermedio/avanzado/experto/maestro |
| notifications | IntegerField      | Contador de notificaciones                    |
| created_at    | DateTimeField     | Auto                                          |
| updated_at    | DateTimeField     | Auto                                          |

**Sistema de niveles por puntos:**
- Principiante: 0–499
- Intermedio: 500–1999
- Avanzado: 2000–4999
- Experto: 5000–9999
- Maestro: 10000+

**Métodos clave:** `add_points()`, `spend_points()`, `update_level()`, `progress_percentage()`, `points_for_next_level()`

### `manager.Project`
| Campo       | Tipo              | Notas                         |
|------------ |-------------------|-------------------------------|
| user        | ForeignKey(CustomUser) | `related_name='projects'` |
| name        | CharField(255)    | Requerido                     |
| description | TextField         | Opcional                      |
| location    | CharField(255)    | Opcional                      |
| start_date  | DateField         | Requerido                     |
| end_date    | DateField         | Opcional                      |
| is_active   | BooleanField      | Default True                  |

### `manager.Notification`
| Campo       | Tipo              | Notas                             |
|------------ |-------------------|-----------------------------------|
| user        | ForeignKey(CustomUser) | `related_name='notifications'` |
| message     | CharField(255)    | Mensaje corto                     |
| description | TextField         | Descripción detallada (opcional)  |
| is_read     | BooleanField      | Default False                     |
| created_at  | DateTimeField     | Auto                              |

---

## 4. URLs y Rutas

### Raíz (`majobacore/urls.py`)
| Ruta              | Vista/Include             | Name              |
|-------------------|---------------------------|--------------------|
| `/admin/`         | admin.site.urls           | —                  |
| `/manager/`       | include('manager.urls')   | —                  |
| `/users/`         | include('users.urls')     | —                  |
| `/`               | index                     | `index`            |
| `/majoba/`        | majoba_view               | `majoba`           |
| `/hormicons/`     | hormicons_view            | `hormicons`        |
| `/constructora/`  | constructora_view         | `constructora`     |
| `/budget/`        | budget_view               | `budget`           |

### Users (`users/urls.py`)
| Ruta                       | Vista              | Name               |
|----------------------------|--------------------|--------------------|
| `/users/create/`           | user_create_view   | `user_create`      |
| `/users/login/`            | custom_login_view  | `login`            |
| `/users/logout/`           | custom_logout_view | `logout`           |
| `/users/profile/`          | profile_view       | `profile`          |
| `/users/modify/<user_id>/` | user_modification  | `user_modify`      |

### Manager (`manager/urls.py`)
| Ruta                                   | Vista                | Name                   |
|----------------------------------------|----------------------|------------------------|
| `/manager/`                            | manager_view         | `manager`              |
| `/manager/admin-dashboard/`            | admin_dashboard_view | `admin_dashboard`      |
| `/manager/list-projects/`              | list_projects_view   | `list_projects`        |
| `/manager/modify-project/<project_id>/`| modify_project_view  | `modify_project`       |
| `/manager/modify/<user_id>/`           | manager_modification | `manager_modification` |
| `/manager/search/`                     | search_users_ajax    | `search`               |
| `/manager/create-project/`             | create_project_view  | `create_project`       |

---

## 5. Roles y Permisos

| Rol         | Accesos                                                                 |
|-------------|-------------------------------------------------------------------------|
| **Staff/Admin** (`is_staff=True`) | Admin dashboard, crear usuarios, modificar ManagerData, búsqueda AJAX, CRUD proyectos, Django Admin |
| **Usuario normal** (`is_staff=False`) | Manager dashboard (su cuenta), ver/crear/editar sus proyectos, ver notificaciones, perfil |

- Login redirige según `is_staff`: staff → `admin_dashboard`, usuario normal → `manager`
- Al crear un usuario se crea automáticamente un `ManagerData` con `create_manager()`
- El admin dashboard requiere `@login_required` + verificación `is_staff`

---

## 6. Entornos y Settings

| Entorno       | Settings Module                        | BD          | Cache      | Debug |
|---------------|----------------------------------------|-------------|------------|-------|
| **Desarrollo** | `majobacore.settings.development`     | SQLite      | DummyCache | True  |
| **Producción** | `majobacore.settings.production`      | PostgreSQL  | Redis      | False |
| **Testing**    | `majobacore.settings.testing`         | SQLite :memory: | DummyCache | False |

**Variable de entorno clave:** `DJANGO_SETTINGS_MODULE`

### Variables de Entorno (.env)
```
SECRET_KEY=...
DEBUG=True/False
DJANGO_SETTINGS_MODULE=majobacore.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=... DB_NAME=... DB_USER=... DB_PASSWORD=... DB_HOST=... DB_PORT=...
REDIS_URL=redis://127.0.0.1:6379/1
EMAIL_HOST=... EMAIL_HOST_USER=... EMAIL_HOST_PASSWORD=...
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CSRF_TRUSTED_ORIGINS=http://localhost:3000,...
```

---

## 7. Comandos de Desarrollo

```bash
# Desde majobacore/ (donde está manage.py)

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
- **Flags activos:** `--reuse-db`, `--nomigrations`, `--strict-markers`
- **Celery en tests:** `CELERY_TASK_ALWAYS_EAGER = True` (ejecución síncrona)

---

## 9. Despliegue (Railway)

- **Builder:** Nixpacks
- **Build:** `pip install -r requirements/production.txt && python manage.py collectstatic --noinput`
- **Release:** `python manage.py migrate --settings=majobacore.settings.production --noinput`
- **Start:** `gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4`
- **Healthcheck:** `/` con timeout de 100s
- **Restart policy:** `ON_FAILURE`, max 10 retries
- **Estáticos:** WhiteNoise (`CompressedManifestStaticFilesStorage`)

---

## 10. Dependencias Principales

| Paquete              | Uso                                           |
|----------------------|-----------------------------------------------|
| Django 5.2+          | Framework web                                 |
| python-decouple      | Gestión de variables de entorno (.env)        |
| Pillow               | Procesamiento de imágenes                     |
| whitenoise           | Servir estáticos en producción                |
| django-extensions    | Utilidades extra para Django                  |
| celery + redis       | Tareas asíncronas (configurado, sin uso visible aún) |
| gunicorn             | Servidor WSGI de producción                   |
| psycopg2-binary      | Driver PostgreSQL                             |
| django-debug-toolbar | Debug en desarrollo                           |
| pytest + pytest-django | Testing                                     |
| black + isort + flake8 | Formateo y linting                          |
| sentry-sdk           | Monitoreo de errores (producción)             |
| boto3 + django-storages | Almacenamiento S3 (producción)             |

---

## 11. Logging

- **Handlers:** console (ERROR), info_file (`logs/info.log`), error_file (`logs/errors.log`)
- **Loggers configurados:** `django`, `majobacore`, `users`, `manager`
- Los loggers de apps (`users`, `manager`) registran a nivel INFO en archivo y ERROR en archivo
- En testing el logging se reduce a WARNING para no ensuciar output

---

## 12. Seguridad

- **Producción:** HTTPS redirect, HSTS (1 año), cookies seguras, X-Frame-Options DENY
- **SecurityHeadersMiddleware** en `majobacore/utils/security.py`: añade headers X-Content-Type-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy
- **CSRF:** cookie HttpOnly, SameSite=Lax, orígenes confiados configurables
- **Sesiones:** backend cache (Redis en prod, DB en dev), 24h de duración, HttpOnly
- **Passwords:** MinimumLengthValidator (8 chars), CommonPasswordValidator, NumericPasswordValidator
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

---

## 14. Patrones Importantes

### Creación de usuario con perfil
Cuando se crea un `CustomUser`, se invoca `create_manager(user)` para generar automáticamente el `ManagerData` asociado. Esto ocurre tanto en el registro como en el login (si no existe).

### Sistema de puntos
Los puntos se modifican con `F()` expressions para operaciones atómicas. Al restar puntos, se usa `models.Case`/`models.When` para prevenir valores negativos. Las notificaciones se crean opcionalmente al modificar puntos.

### Búsqueda AJAX
`search_users_ajax` devuelve JSON paginado. Solo accesible por staff. Filtra por username, first_name, last_name con `icontains`.

### Redirección post-login
Staff → `admin_dashboard` | Usuario normal → `manager`

---

## 15. Notas para Agentes

1. **Directorio de trabajo:** Los comandos Django se ejecutan desde `majobacore/` (donde está `manage.py`)
2. **No hay API REST formal:** Aunque DRF está mencionado en el README, actualmente NO está instalado ni configurado. Las vistas son server-side rendered con una excepción AJAX (`search_users_ajax`)
3. **Celery configurado pero sin tareas:** Las dependencias están instaladas y el testing lo soporta (`ALWAYS_EAGER`), pero no hay tareas Celery definidas aún
4. **Sistema operativo del desarrollador:** Windows
5. **Sin Docker:** El proyecto no usa Docker; se ejecuta directamente con venv en Windows
6. **STATICFILES_DIRS** apunta a `static/` en la raíz del proyecto Django
7. **Archivos de log** se guardan en `logs/` — asegurarse de que el directorio exista
8. **El admin de Django** está en `/admin/` y es funcional con `CustomUserAdmin` personalizado
9. **Bootstrap-like CSS:** Los formularios usan clases como `form-control`; no hay framework CSS formal instalado, los estilos son custom
10. **Al modificar modelos:** siempre ejecutar `makemigrations` y `migrate`; las migraciones existentes están en cada app
