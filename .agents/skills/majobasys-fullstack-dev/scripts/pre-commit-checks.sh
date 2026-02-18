#!/bin/bash
# Pre-commit checks para MajobaSYS
# Ejecutar antes de hacer commit para validar código

echo "🔍 Ejecutando validaciones pre-commit..."
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de errores
ERRORS=0

# 1. Django check
echo "📋 1. Verificando configuración de Django..."
cd majobacore
python manage.py check --settings=majobacore.settings.development
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Django check passed${NC}"
else
    echo -e "${RED}✗ Django check failed${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 2. Django check --deploy
echo "🚀 2. Verificando configuración de producción..."
python manage.py check --deploy --settings=majobacore.settings.production
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Production check passed${NC}"
else
    echo -e "${YELLOW}⚠ Production check tiene warnings (revisar antes de deploy)${NC}"
fi
echo ""

# 3. Verificar migraciones pendientes
echo "🗄️  3. Verificando migraciones..."
python manage.py makemigrations --check --dry-run --settings=majobacore.settings.development
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ No hay migraciones pendientes${NC}"
else
    echo -e "${RED}✗ Hay migraciones pendientes. Ejecuta: python manage.py makemigrations${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 4. Ejecutar tests (si existen)
echo "🧪 4. Ejecutando tests..."
python manage.py test --parallel --settings=majobacore.settings.testing
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 5. Verificar sintaxis Python (opcional, requiere flake8)
if command -v flake8 &> /dev/null; then
    echo "🐍 5. Verificando sintaxis Python..."
    cd ..
    flake8 majobacore --exclude=migrations,venv,env --max-line-length=100
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python syntax OK${NC}"
    else
        echo -e "${YELLOW}⚠ Hay warnings de flake8 (no bloqueante)${NC}"
    fi
    echo ""
fi

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Todas las validaciones pasaron${NC}"
    echo "✅ Listo para commit!"
    exit 0
else
    echo -e "${RED}✗ $ERRORS validaciones fallaron${NC}"
    echo "❌ Corrige los errores antes de hacer commit"
    exit 1
fi
