# Plan del Proyecto: App Móvil MajobaSyS + API REST

> Documento de planificación para la extensión móvil del sistema MajobaSyS.
> Branch: `feature/api-rest`
> Fecha de creación: 2026-03-17

---

## Resumen de Decisiones Técnicas

| Aspecto | Decisión | Justificación |
|---------|----------|---------------|
| **Framework móvil** | Expo (React Native) | DX superior, OTA updates, builds en la nube sin Xcode/Android Studio local |
| **Lenguaje** | TypeScript | Tipado estático, mejor DX, consistencia con el ecosistema React |
| **Estilos** | NativeWind (TailwindCSS para RN) | Reutiliza conocimiento de Tailwind, utility-first, responsive nativo |
| **Navegación** | React Navigation | Estándar de facto en React Native, soporte nativo de stacks/tabs/drawers |
| **Estado global** | Zustand | Ligero, sin boilerplate, API simple, compatible con persist para tokens |
| **Autenticación API** | JWT con SimpleJWT | Stateless, ideal para mobile, refresh token automático, estándar de la industria |
| **Estructura backend** | App `api/` modular por dominio | Separación limpia del backend web existente, versionado `/api/v1/` |
| **Filtrado API** | django-filter | Integración nativa con DRF, filtrado declarativo |

---

## Fase 1: API REST en Django

### 1A — Infraestructura Inicial

- [ ] Crear branch `feature/api-rest` desde `main`
- [ ] Crear directorio `mobile/` en la raíz del repositorio
- [ ] Crear `mobile/PLAN.md` con el plan completo del proyecto
- [ ] Agregar `watchPatterns` a `railway.toml` para excluir `mobile/` del deploy
- [ ] Verificar que Railway solo redeploya con cambios en archivos del backend

### 1B — Dependencias y Settings

- [ ] Agregar a `requirements/base.txt`:
  - `djangorestframework`
  - `djangorestframework-simplejwt`
  - `django-filter`
- [ ] Configurar `base.py`:
  - Agregar `rest_framework`, `rest_framework_simplejwt`, `django_filters` a `INSTALLED_APPS`
  - Configurar `REST_FRAMEWORK` (default auth, permission, pagination, throttle, filter backend, renderers, datetime format)
  - Configurar `SIMPLE_JWT` (access lifetime, refresh lifetime, rotate refresh, blacklist, algorithm, auth header, token classes)
- [ ] Configurar `production.py`:
  - Ajustar renderers (solo JSON en producción)
  - Configurar throttle rates de producción
- [ ] Configurar `testing.py`:
  - Agregar overrides para DRF en tests (force auth, desactivar throttling)
- [ ] Configurar `development.py`:
  - Habilitar BrowsableAPI renderer para desarrollo
  - Throttle rates más permisivos
- [ ] Ejecutar `pip install -r requirements/development.txt` y verificar instalación
- [ ] Ejecutar `python manage.py check` — sin errores

### 1C — Refactor de Lógica de Negocio

- [ ] Crear `manager/services.py`
- [ ] Mover la función `create_manager()` de `manager/views.py` a `manager/services.py`
- [ ] Actualizar imports en `manager/views.py` y `users/views.py`
- [ ] Ejecutar tests existentes — sin regresiones
- [ ] Verificar que el flujo de creación de usuario + ManagerData sigue funcionando

### 1D — Crear App `api/` con Estructura Modular

- [ ] Crear app Django `api/` en la raíz del proyecto
- [ ] Estructura de archivos:

```
api/
├── __init__.py
├── apps.py
├── urls.py                    ← Router principal: include v1/
├── permissions.py             ← Permisos compartidos (IsOwner, IsStaffOrOwner, etc.)
├── pagination.py              ← Paginación estándar del proyecto
├── throttling.py              ← Throttle classes personalizados
├── v1/
│   ├── __init__.py
│   ├── urls.py                ← Agrupa todos los routers de v1
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── serializers.py     ← LoginSerializer, RegisterSerializer, ChangePasswordSerializer
│   │   ├── views.py           ← LoginView, RegisterView, LogoutView, RefreshView, ChangePasswordView
│   │   └── urls.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── serializers.py     ← UserSerializer, UserDetailSerializer, UserUpdateSerializer
│   │   ├── views.py           ← UserViewSet (admin), ProfileView (propio)
│   │   └── urls.py
│   ├── manager/
│   │   ├── __init__.py
│   │   ├── serializers.py     ← ManagerDataSerializer, ManagerDataUpdateSerializer
│   │   ├── views.py           ← ManagerDataViewSet, DashboardView
│   │   └── urls.py
│   ├── projects/
│   │   ├── __init__.py
│   │   ├── serializers.py     ← ProjectSerializer, ProjectCreateSerializer, ProjectListSerializer
│   │   ├── views.py           ← ProjectViewSet
│   │   ├── filters.py         ← ProjectFilter (por cliente, activo, fechas)
│   │   └── urls.py
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── serializers.py     ← ClientSerializer, ClientCreateSerializer
│   │   ├── views.py           ← ClientViewSet
│   │   └── urls.py
│   └── notifications/
│       ├── __init__.py
│       ├── serializers.py     ← NotificationSerializer
│       ├── views.py           ← NotificationViewSet (list, mark_read, mark_all_read)
│       └── urls.py
```

- [ ] Registrar `api` en `INSTALLED_APPS` de `base.py`
- [ ] Agregar `path('api/', include('api.urls'))` en `majobacore/urls.py`
- [ ] Ejecutar `python manage.py check` — sin errores

### 1E — Endpoints: Serializers + Views + URLs

#### Auth (`api/v1/auth/`)

- [ ] `LoginSerializer` — valida username + password, devuelve tokens JWT
- [ ] `RegisterSerializer` — crea usuario + ManagerData (usando `create_manager` de services.py)
- [ ] `ChangePasswordSerializer` — valida old_password + new_password con validators de Django
- [ ] `LoginView` (POST) — autenticación, devuelve access + refresh tokens
- [ ] `LogoutView` (POST) — blacklist del refresh token
- [ ] `RefreshView` (POST) — renueva access token
- [ ] `RegisterView` (POST) — solo staff puede crear usuarios (consistente con web)
- [ ] `ChangePasswordView` (PUT) — usuario autenticado cambia su password
- [ ] URLs registradas y accesibles

#### Users (`api/v1/users/`)

- [ ] `UserSerializer` — representación básica (id, username, first_name, last_name, email)
- [ ] `UserDetailSerializer` — todos los campos relevantes
- [ ] `UserUpdateSerializer` — campos editables con validación
- [ ] `ProfileView` (GET, PUT/PATCH) — perfil del usuario autenticado
- [ ] `UserViewSet` (CRUD) — solo staff, con filtros y búsqueda
- [ ] URLs registradas y accesibles

#### Manager (`api/v1/manager/`)

- [ ] `ManagerDataSerializer` — puntos, nivel, progreso, notificaciones
- [ ] `ManagerDataUpdateSerializer` — solo staff puede modificar puntos/nivel
- [ ] `DashboardView` (GET) — datos consolidados del usuario (perfil + manager + stats)
- [ ] `ManagerDataViewSet` — staff: listar/editar todos; usuario: solo su ManagerData
- [ ] URLs registradas y accesibles

#### Projects (`api/v1/projects/`)

- [ ] `ProjectSerializer` — representación completa con client anidado
- [ ] `ProjectCreateSerializer` — validación con soporte para `new_client_name` inline
- [ ] `ProjectListSerializer` — representación ligera para listados
- [ ] `ProjectFilter` — filtrar por client, is_active, rango de fechas
- [ ] `ProjectViewSet` — CRUD completo, filtrado a proyectos del usuario autenticado
- [ ] URLs registradas y accesibles

#### Clients (`api/v1/clients/`)

- [ ] `ClientSerializer` — representación completa
- [ ] `ClientCreateSerializer` — validación de nombre único por usuario
- [ ] `ClientViewSet` — CRUD filtrado a clientes del usuario autenticado
- [ ] URLs registradas y accesibles

#### Notifications (`api/v1/notifications/`)

- [ ] `NotificationSerializer` — mensaje, descripción, is_read, time_elapsed
- [ ] `NotificationViewSet` — list (con paginación), retrieve
- [ ] Action `mark_read` (POST) — marcar notificación individual como leída
- [ ] Action `mark_all_read` (POST) — marcar todas las notificaciones como leídas
- [ ] Action `unread_count` (GET) — devolver conteo de no leídas
- [ ] URLs registradas y accesibles

### 1F — Seguridad y Configuración Transversal

- [ ] Crear `api/permissions.py`:
  - `IsOwner` — el recurso pertenece al usuario autenticado
  - `IsStaffOrOwner` — staff o dueño del recurso
  - `IsStaffUser` — solo staff
- [ ] Crear `api/pagination.py`:
  - `StandardPagination` — PageNumberPagination con page_size configurable (default 20)
- [ ] Crear `api/throttling.py`:
  - `LoginRateThrottle` — rate limit específico para login (5/min)
  - `RegisterRateThrottle` — rate limit para registro (3/min)
  - `BurstRateThrottle` — rate limit general burst (60/min)
  - `SustainedRateThrottle` — rate limit general sostenido (1000/día)
- [ ] Ajustar `SecurityHeadersMiddleware` en `majobacore/utils/security.py`:
  - Agregar headers específicos para API (Access-Control headers si CORS activo)
  - Asegurar que no interfiera con preflight OPTIONS requests
- [ ] Configurar CORS en `production.py`:
  - Asegurar que `django-cors-headers` está activo cuando `CORS_ALLOWED_ORIGINS` está configurado
  - Permitir headers de Authorization
- [ ] Verificar que los endpoints de health check no requieren autenticación
- [ ] Ejecutar `python manage.py check --deploy --settings=majobacore.settings.production` — sin errores críticos

### 1G — Tests y Validación

- [ ] Crear `api/tests/`:
  - `__init__.py`
  - `test_auth.py` — tests de login, registro, logout, refresh, change password
  - `test_users.py` — tests de perfil, CRUD usuarios (staff)
  - `test_manager.py` — tests de dashboard, ManagerData
  - `test_projects.py` — tests de CRUD proyectos, filtros, creación inline de client
  - `test_clients.py` — tests de CRUD clientes
  - `test_notifications.py` — tests de listado, mark_read, mark_all_read, unread_count
  - `test_permissions.py` — tests de permisos (owner, staff, anónimo)
  - `test_throttling.py` — tests de rate limiting
- [ ] Fixtures/factories para datos de prueba
- [ ] Ejecutar `pytest api/` — todos los tests pasan
- [ ] Ejecutar `pytest` — todos los tests del proyecto pasan (sin regresiones)
- [ ] Verificar cobertura mínima del 80% en la app `api/`
- [ ] Test manual con cURL o httpie de los endpoints principales
- [ ] Verificar que la API funciona con el BrowsableAPI en desarrollo

---

## Fase 2: App React Native Base + Autenticación

### 2A — Inicialización del Proyecto Expo

- [ ] Ejecutar `npx create-expo-app@latest mobile/MajobaSySApp --template blank-typescript`
- [ ] Instalar dependencias core:
  - `nativewind` + `tailwindcss` (configurar)
  - `react-native-reanimated`
  - `react-native-safe-area-context`
  - `react-native-screens`
- [ ] Instalar navegación:
  - `@react-navigation/native`
  - `@react-navigation/native-stack`
  - `@react-navigation/bottom-tabs`
- [ ] Instalar estado y networking:
  - `zustand` + `zustand/middleware` (persist)
  - `axios`
  - `@react-native-async-storage/async-storage`
- [ ] Configurar TypeScript estricto (`tsconfig.json`)
- [ ] Configurar NativeWind (`tailwind.config.js`, `babel.config.js`)
- [ ] Configurar path aliases (`@/` → `src/`)
- [ ] Verificar que la app arranca sin errores: `npx expo start`

### 2B — API Client y Auth Store

- [ ] Crear `src/services/api.ts` — instancia de Axios con baseURL configurable
- [ ] Crear `src/services/interceptors.ts`:
  - Request interceptor: agregar Authorization header con access token
  - Response interceptor: detectar 401, intentar refresh, reintentar request original
  - Manejo de refresh token expirado → forzar logout
- [ ] Crear `src/stores/authStore.ts` (Zustand):
  - Estado: `user`, `accessToken`, `refreshToken`, `isAuthenticated`, `isLoading`
  - Acciones: `login()`, `logout()`, `refreshToken()`, `loadStoredAuth()`
  - Persist: guardar tokens en AsyncStorage
- [ ] Crear types: `src/types/auth.ts`, `src/types/user.ts`
- [ ] Test manual: login contra API, almacenar token, refresh automático

### 2C — Navegación y Pantalla de Login

- [ ] Crear estructura de navegación:
  - `RootNavigator` — decide entre AuthStack y AppStack según `isAuthenticated`
  - `AuthStack` — contiene LoginScreen (y futuro RegisterScreen)
  - `AppStack` — contiene BottomTabs (Dashboard, Proyectos, Perfil)
- [ ] Crear `LoginScreen`:
  - Formulario con username + password
  - Validación de campos
  - Indicador de loading
  - Manejo de errores (credenciales inválidas, red, servidor)
  - Diseño con NativeWind alineado al branding de MajobaSyS
- [ ] Crear `SplashScreen`:
  - Verificar token almacenado al iniciar la app
  - Intentar refresh si hay token guardado
  - Navegar a Login o Dashboard según resultado
- [ ] Verificar flujo completo: splash → login → dashboard → logout → login

### 2D — Agentes Locales para Desarrollo Móvil

- [ ] Crear `mobile/.agents/skills/` con skills específicas:
  - `expo-react-native/` — convenciones Expo, estructura de proyecto
  - `nativewind/` — patrones NativeWind, responsive, dark mode
  - `zustand-state/` — patrones Zustand, slices, persist
- [ ] Crear `mobile/AGENTS.md` — referencia para agentes trabajando en la app móvil

---

## Fase 3: Features Completas

### 3A — Dashboard y Perfil

- [ ] Crear `DashboardScreen`:
  - Datos del ManagerData (puntos, nivel, barra de progreso)
  - Proyectos activos (resumen, últimos 5)
  - Notificaciones recientes (últimas 3, con badge de no leídas)
  - Pull-to-refresh
- [ ] Crear `ProfileScreen`:
  - Mostrar datos del usuario
  - Editar perfil (nombre, teléfono, profesión, dirección)
  - Cambiar contraseña
  - Cerrar sesión
- [ ] Crear `ChangePasswordScreen`:
  - Formulario con validación
  - Confirmación de contraseña
  - Feedback de éxito/error

### 3B — CRUD de Proyectos y Clientes

- [ ] Crear `ProjectsListScreen`:
  - Lista paginada de proyectos
  - Filtro por cliente (dropdown)
  - Filtro por estado (activo/inactivo)
  - Búsqueda por nombre
  - Pull-to-refresh + infinite scroll
- [ ] Crear `ProjectDetailScreen`:
  - Datos completos del proyecto
  - Información del cliente asociado
  - Opciones: editar, desactivar
- [ ] Crear `ProjectFormScreen` (crear/editar):
  - Formulario con validación
  - Selector de cliente existente
  - Opción de crear cliente nuevo inline
  - Date pickers para fechas
- [ ] Crear `ClientsListScreen`:
  - Lista de clientes del usuario
  - Crear cliente nuevo
  - Ver proyectos asociados

### 3C — Notificaciones

- [ ] Crear `NotificationsScreen`:
  - Lista paginada de notificaciones
  - Indicador visual de leída/no leída
  - Swipe para marcar como leída
  - Botón "Marcar todas como leídas"
  - Pull-to-refresh
- [ ] Implementar badge de notificaciones:
  - Conteo de no leídas en el tab de notificaciones
  - Polling periódico (cada 30s) o al volver a la app
- [ ] Feedback visual al marcar como leída

### 3D — Pulido UI y UX

- [ ] Implementar loading states consistentes (skeletons o spinners)
- [ ] Implementar error handling global:
  - Error boundaries para crashes
  - Toast/Snackbar para errores de red
  - Pantalla de error con retry
- [ ] Implementar empty states (sin proyectos, sin notificaciones, etc.)
- [ ] Implementar animaciones sutiles (transitions entre pantallas, feedback táctil)
- [ ] Revisar accesibilidad (labels, contrast, font scaling)
- [ ] Revisar performance (listas virtualizadas, memoización)
- [ ] Tema visual coherente con el branding web de MajobaSyS

---

## Fase 4 (Futura): Push Notifications

> Esta fase se implementará después de las fases 1-3.

- [ ] Configurar Expo Push Notifications
- [ ] Crear modelo `DeviceToken` en Django para almacenar tokens de dispositivos
- [ ] Endpoint API para registrar/desregistrar device tokens
- [ ] Integrar envío de push notifications con el sistema de `Notification` existente
- [ ] Tarea Celery para enviar push notifications en background
- [ ] Manejo de notificaciones en foreground, background y app cerrada
- [ ] Deep linking desde notificaciones a pantallas específicas

---

## Estructura de Archivos de la App Móvil

```
mobile/
├── PLAN.md                          ← Este archivo
├── AGENTS.md                        ← Referencia para agentes (Fase 2D)
├── .agents/
│   └── skills/                      ← Skills específicas para desarrollo móvil
│
└── MajobaSySApp/                    ← Proyecto Expo
    ├── app.json                     ← Configuración Expo
    ├── babel.config.js
    ├── tailwind.config.js           ← Configuración NativeWind
    ├── tsconfig.json
    ├── package.json
    ├── .env                         ← Variables de entorno locales (API_URL, etc.)
    ├── .env.example
    │
    ├── assets/                      ← Imágenes, fuentes, iconos
    │   ├── images/
    │   ├── fonts/
    │   └── icons/
    │
    └── src/
        ├── app/                     ← Entry point y providers
        │   ├── App.tsx
        │   └── providers.tsx
        │
        ├── navigation/             ← Navegación
        │   ├── RootNavigator.tsx
        │   ├── AuthStack.tsx
        │   ├── AppStack.tsx
        │   └── BottomTabs.tsx
        │
        ├── screens/                ← Pantallas
        │   ├── auth/
        │   │   ├── LoginScreen.tsx
        │   │   └── SplashScreen.tsx
        │   ├── dashboard/
        │   │   └── DashboardScreen.tsx
        │   ├── projects/
        │   │   ├── ProjectsListScreen.tsx
        │   │   ├── ProjectDetailScreen.tsx
        │   │   └── ProjectFormScreen.tsx
        │   ├── clients/
        │   │   └── ClientsListScreen.tsx
        │   ├── notifications/
        │   │   └── NotificationsScreen.tsx
        │   └── profile/
        │       ├── ProfileScreen.tsx
        │       └── ChangePasswordScreen.tsx
        │
        ├── components/             ← Componentes reutilizables
        │   ├── ui/                 ← Primitivos (Button, Input, Card, Badge, etc.)
        │   ├── forms/              ← Componentes de formulario
        │   ├── layout/             ← Header, Container, SafeArea
        │   └── shared/             ← Loading, EmptyState, ErrorBoundary
        │
        ├── services/               ← Comunicación con API
        │   ├── api.ts              ← Instancia Axios + config
        │   ├── interceptors.ts     ← JWT interceptors
        │   ├── authService.ts      ← login, register, logout, refresh
        │   ├── userService.ts      ← perfil, update
        │   ├── projectService.ts   ← CRUD proyectos
        │   ├── clientService.ts    ← CRUD clientes
        │   └── notificationService.ts
        │
        ├── stores/                 ← Zustand stores
        │   ├── authStore.ts
        │   ├── projectStore.ts
        │   ├── notificationStore.ts
        │   └── uiStore.ts          ← Loading global, toasts, theme
        │
        ├── types/                  ← Tipos TypeScript
        │   ├── auth.ts
        │   ├── user.ts
        │   ├── project.ts
        │   ├── client.ts
        │   ├── notification.ts
        │   ├── manager.ts
        │   ├── api.ts              ← Tipos de respuesta API, errores, paginación
        │   └── navigation.ts       ← Tipos de params de navegación
        │
        ├── hooks/                  ← Custom hooks
        │   ├── useAuth.ts
        │   ├── useProjects.ts
        │   ├── useNotifications.ts
        │   └── useRefreshOnFocus.ts
        │
        ├── utils/                  ← Utilidades
        │   ├── formatters.ts       ← Fechas, números, texto
        │   ├── validators.ts       ← Validación de formularios
        │   └── constants.ts        ← Colores, tamaños, keys de storage
        │
        └── theme/                  ← Tema y estilos
            ├── colors.ts
            ├── typography.ts
            └── spacing.ts
```

---

## Endpoints API Planificados

### Auth (`/api/v1/auth/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| POST | `/api/v1/auth/login/` | Obtener tokens JWT | Público |
| POST | `/api/v1/auth/register/` | Crear usuario + ManagerData | Staff |
| POST | `/api/v1/auth/logout/` | Blacklist refresh token | Autenticado |
| POST | `/api/v1/auth/refresh/` | Renovar access token | Público (con refresh token) |
| PUT | `/api/v1/auth/change-password/` | Cambiar contraseña | Autenticado |

### Users (`/api/v1/users/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/v1/users/profile/` | Obtener perfil propio | Autenticado |
| PUT/PATCH | `/api/v1/users/profile/` | Actualizar perfil propio | Autenticado |
| GET | `/api/v1/users/` | Listar usuarios | Staff |
| GET | `/api/v1/users/{id}/` | Detalle de usuario | Staff |
| PUT/PATCH | `/api/v1/users/{id}/` | Actualizar usuario | Staff |
| DELETE | `/api/v1/users/{id}/` | Desactivar usuario | Staff |

### Manager (`/api/v1/manager/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/v1/manager/dashboard/` | Dashboard consolidado | Autenticado |
| GET | `/api/v1/manager/` | Listar ManagerData | Staff |
| GET | `/api/v1/manager/{id}/` | Detalle ManagerData | Staff o Owner |
| PUT/PATCH | `/api/v1/manager/{id}/` | Modificar puntos/nivel | Staff |

### Projects (`/api/v1/projects/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/v1/projects/` | Listar proyectos del usuario | Autenticado |
| POST | `/api/v1/projects/` | Crear proyecto | Autenticado |
| GET | `/api/v1/projects/{id}/` | Detalle de proyecto | Owner |
| PUT/PATCH | `/api/v1/projects/{id}/` | Actualizar proyecto | Owner |
| DELETE | `/api/v1/projects/{id}/` | Eliminar proyecto | Owner |

### Clients (`/api/v1/clients/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/v1/clients/` | Listar clientes del usuario | Autenticado |
| POST | `/api/v1/clients/` | Crear cliente | Autenticado |
| GET | `/api/v1/clients/{id}/` | Detalle de cliente | Owner |
| PUT/PATCH | `/api/v1/clients/{id}/` | Actualizar cliente | Owner |
| DELETE | `/api/v1/clients/{id}/` | Eliminar cliente | Owner |

### Notifications (`/api/v1/notifications/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/v1/notifications/` | Listar notificaciones | Autenticado |
| GET | `/api/v1/notifications/{id}/` | Detalle de notificación | Owner |
| POST | `/api/v1/notifications/{id}/mark-read/` | Marcar como leída | Owner |
| POST | `/api/v1/notifications/mark-all-read/` | Marcar todas como leídas | Autenticado |
| GET | `/api/v1/notifications/unread-count/` | Conteo de no leídas | Autenticado |

---

## Notas para Agentes

1. **Branch de trabajo:** Todo el desarrollo de la API y la app móvil se realiza en `feature/api-rest` y sus sub-branches
2. **Directorio de trabajo Django:** La raíz del repositorio (donde está `manage.py`). La app `api/` se crea al mismo nivel que `users/` y `manager/`
3. **Directorio de trabajo móvil:** `mobile/MajobaSySApp/`
4. **No romper la web existente:** La API es una extensión, no un reemplazo. Las vistas web, templates y URLs existentes deben seguir funcionando exactamente igual
5. **`create_manager` compartido:** Tanto la web como la API usan la misma función de `manager/services.py` para crear ManagerData
6. **Permisos consistentes:** Los permisos de la API reflejan los roles existentes (staff vs usuario normal). Staff puede todo, usuario normal solo gestiona sus propios recursos
7. **Versionado de API:** Se usa `/api/v1/` desde el inicio para permitir futuras versiones sin romper clientes existentes
8. **Idioma del código:** Código en inglés, documentación y mensajes de usuario en español (consistente con el proyecto existente)
9. **Railway deploy:** `mobile/` está excluido de `watchPatterns` — cambios en la app móvil no disparan redeploy del backend
10. **Testing:** La app `api/` debe incluirse en la configuración de coverage de `pytest.ini`
11. **Orden de implementación:** Seguir estrictamente las fases: primero la API completa con tests, después la app móvil
12. **SimpleJWT blacklist:** Requiere la app `rest_framework_simplejwt.token_blacklist` en `INSTALLED_APPS` y una migración
