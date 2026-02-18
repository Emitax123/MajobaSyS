# MajobaSYS Full Stack Django Developer Agent

Agente especializado para el desarrollo Full Stack del proyecto **MajobaSYS**, un sistema de gamificación empresarial construido con Django.

## 🎯 Propósito

Este agente asiste en todas las tareas de desarrollo del proyecto MajobaSYS, desde el backend Django hasta las APIs REST, siguiendo las mejores prácticas y estándares del proyecto.

## ✨ Características

- **Asistente Guiado**: Pregunta y clarifica antes de implementar
- **Validaciones Automáticas**: Ejecuta checks después de cada cambio
- **Documentación en Español**: Todos los docstrings y comentarios en español
- **Optimización PostgreSQL**: Diseñado para producción con PostgreSQL
- **JWT Ready**: Preparado para autenticación móvil
- **Railway Deploy**: Configuración lista para Railway

## 📚 Documentación

### Archivos Principales

- **[SKILL.md](SKILL.md)** - Configuración completa del agente y workflows
- **[reference/project-context.md](reference/project-context.md)** - Contexto del proyecto MajobaSYS
- **[reference/coding-standards.md](reference/coding-standards.md)** - Estándares de código
- **[reference/api-guidelines.md](reference/api-guidelines.md)** - Diseño de APIs REST
- **[reference/railway-deploy.md](reference/railway-deploy.md)** - Deploy en Railway
- **[reference/jwt-auth-setup.md](reference/jwt-auth-setup.md)** - Autenticación JWT
- **[reference/common-workflows.md](reference/common-workflows.md)** - Workflows comunes

### Scripts Útiles

- **[scripts/pre-commit-checks.sh](scripts/pre-commit-checks.sh)** - Validaciones pre-commit
- **[scripts/run-tests.sh](scripts/run-tests.sh)** - Suite de tests
- **[scripts/railway-deploy-check.sh](scripts/railway-deploy-check.sh)** - Verificar config Railway

## 🚀 Cómo Usar

El agente se activa automáticamente cuando trabajas en el proyecto MajobaSYS. Simplemente:

1. **Describe tu tarea**: "Necesito crear una API REST para el sistema de badges"
2. **El agente analizará** el contexto, consultará skills relevantes
3. **Te propondrá opciones** con explicaciones
4. **Implementará** siguiendo mejores prácticas
5. **Validará automáticamente** con checks de Django

## 🛠️ Skills Integradas

Este agente integra automáticamente:

- ✅ **django-expert** - Conocimiento experto Django
- ✅ **django-rest-framework** - APIs con DRF
- ✅ **django-patterns** - Patrones de diseño
- ✅ **django-security** - Seguridad
- ✅ **api-design-principles** - Diseño de APIs
- ✅ **python-best-practices** - Mejores prácticas Python
- ✅ **postgresql-table-design** - Optimización PostgreSQL
- ✅ **test-driven-development** - TDD
- ✅ **systematic-debugging** - Debugging
- ✅ **deployment** (Railway) - Deploy Railway
- ✅ **database** (Railway) - PostgreSQL Railway
- ✅ **jwt-security** - Seguridad JWT
- ✅ **api-security-best-practices** - Seguridad APIs

## 📋 Capacidades

### Backend Development
- Crear/modificar modelos Django
- Implementar vistas (CBV y FBV)
- Configurar URLs y routing
- Signals y middleware
- Optimización de queries

### API REST
- Serializers con validaciones
- ViewSets y Routers
- Autenticación JWT
- Permisos y políticas
- Documentación automática

### Base de Datos
- Diseño optimizado para PostgreSQL
- Migraciones complejas
- Índices estratégicos
- Validadores en campos

### Testing
- Tests unitarios
- Tests de integración
- Fixtures y factories
- Coverage reports

### Seguridad
- OWASP best practices
- JWT security
- CSRF/XSS protection
- Validación de settings

### Deployment
- Railway configuration
- PostgreSQL setup
- Static files serving
- Health checks

## 🔧 Workflow del Agente

### 1. Análisis 🔍
- Analiza la solicitud
- Revisa archivos relacionados
- Consulta skills relevantes
- Verifica migraciones

### 2. Planificación 💭
- Propone opciones
- Explica decisiones
- Espera aprobación

### 3. Implementación 💻
- Sigue mejores prácticas
- Agrega logging
- Documenta en español
- Crea migraciones

### 4. Validación ✅
```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check
python manage.py test
```

### 5. Documentación 📝
- Docstrings completos
- Comentarios inline
- Actualiza CHANGELOG

## 🎓 Conocimiento del Proyecto

### Apps
- **users** - Gestión de usuarios (CustomUser)
- **manager** - Sistema de gamificación (CustomManager)

### Modelos Principales
- **CustomUser** - Usuario sin email obligatorio
- **CustomManager** - Perfil de gamificación con puntos y niveles

### Sistema de Niveles
| Nivel | Puntos Lifetime |
|-------|----------------|
| Bronze | 0-499 |
| Silver | 500-1,999 |
| Gold | 2,000-4,999 |
| Platinum | 5,000-9,999 |
| Diamond | 10,000+ |

### Stack Tecnológico
- Django 5.2
- PostgreSQL (producción)
- Redis (cache)
- Django REST Framework
- JWT authentication
- Railway (deploy)

## 🔍 Detección Automática

El agente detecta y corrige:

- ✅ N+1 query problems
- ✅ Falta de índices
- ✅ Validaciones faltantes
- ✅ Secrets hardcodeados
- ✅ Permisos faltantes en APIs
- ✅ Código duplicado
- ✅ Security issues

## 📊 Validaciones Automáticas

Después de cada implementación ejecuta:

```bash
✓ Django check
✓ Django check --deploy
✓ Verificar migraciones pendientes
✓ Ejecutar tests
✓ Verificar sintaxis Python
```

## 🌐 Futuras Expansiones

El agente está preparado para:

- 🔜 API REST completa para React Native
- 🔜 Deploy en Railway con PostgreSQL
- 🔜 Autenticación JWT para mobile
- 🔜 Push notifications
- 🔜 Sincronización offline

## 🤝 Convenciones del Proyecto

### Imports Ordenados
```python
# stdlib → django → third-party → local
import logging
from django.db import models
from rest_framework import serializers
from users.models import CustomUser
```

### Logger Siempre
```python
logger = logging.getLogger(__name__)
logger.info(f"Usuario {user.username} creó recurso")
```

### Validadores Obligatorios
```python
puntos = models.IntegerField(
    default=0,
    validators=[MinValueValidator(0)]
)
```

### Docstrings en Español
```python
def agregar_puntos(self, cantidad):
    """
    Agregar puntos al usuario.
    
    Args:
        cantidad (int): Puntos a agregar
    
    Returns:
        bool: True si exitoso
    """
```

## 📞 Soporte

- **Documentación completa**: Ver archivos en `reference/`
- **Scripts útiles**: Ver archivos en `scripts/`
- **Changelog del proyecto**: `MEJORAS_IMPLEMENTADAS.md`

## 📝 Versión

**Versión**: 1.0.0  
**Última actualización**: Febrero 2026  
**Proyecto**: MajobaSYS  
**Mantenedor**: Equipo MajobaSYS

---

**¡El agente está listo para asistirte en el desarrollo de MajobaSYS!** 🚀
