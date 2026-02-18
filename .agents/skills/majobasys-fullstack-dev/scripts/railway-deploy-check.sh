#!/bin/bash
# Verificar que el proyecto está listo para deploy en Railway

echo "🚂 Verificando configuración para Railway..."
echo ""

ERRORS=0

# 1. Verificar archivos requeridos
echo "📁 1. Verificando archivos requeridos..."
FILES=("requirements.txt" "Procfile" "runtime.txt" "railway.json")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file existe"
    else
        echo "  ✗ $file NO existe"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# 2. Verificar requirements.txt contiene dependencias clave
echo "📦 2. Verificando dependencias..."
DEPS=("Django" "gunicorn" "psycopg2-binary" "whitenoise")
for dep in "${DEPS[@]}"; do
    if grep -q "$dep" requirements.txt; then
        echo "  ✓ $dep en requirements.txt"
    else
        echo "  ✗ $dep NO está en requirements.txt"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# 3. Verificar Procfile
echo "🔧 3. Verificando Procfile..."
if [ -f "Procfile" ]; then
    if grep -q "gunicorn" Procfile; then
        echo "  ✓ Procfile contiene comando gunicorn"
    else
        echo "  ✗ Procfile no contiene gunicorn"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# 4. Verificar settings de producción
echo "⚙️  4. Verificando settings de producción..."
cd majobacore
python manage.py check --deploy --settings=majobacore.settings.production
if [ $? -eq 0 ]; then
    echo "  ✓ Settings de producción OK"
else
    echo "  ⚠ Settings de producción tiene warnings"
fi
echo ""

# 5. Verificar SECRET_KEY no está hardcodeada
echo "🔐 5. Verificando SECRET_KEY..."
if grep -r "SECRET_KEY.*=.*'django-insecure" majobacore/settings/; then
    echo "  ✗ SECRET_KEY hardcodeada encontrada"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ SECRET_KEY parece estar en variables de entorno"
fi
echo ""

# 6. Verificar migraciones
echo "🗄️  6. Verificando migraciones..."
python manage.py makemigrations --check --dry-run --settings=majobacore.settings.production
if [ $? -eq 0 ]; then
    echo "  ✓ No hay migraciones pendientes"
else
    echo "  ✗ Hay migraciones pendientes"
    ERRORS=$((ERRORS + 1))
fi
cd ..
echo ""

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Proyecto listo para deploy en Railway!"
    echo ""
    echo "Próximos pasos:"
    echo "1. git push origin main (para deploy automático)"
    echo "2. railway run python majobacore/manage.py migrate"
    echo "3. railway run python majobacore/manage.py createsuperuser"
    exit 0
else
    echo "❌ $ERRORS problemas encontrados"
    echo "Corrige los errores antes de deployar"
    exit 1
fi
