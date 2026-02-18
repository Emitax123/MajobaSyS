#!/bin/bash
# Script para ejecutar suite completa de tests

echo "🧪 Ejecutando suite de tests de MajobaSYS..."
echo ""

cd majobacore

# Con coverage
if command -v coverage &> /dev/null; then
    echo "📊 Ejecutando tests con coverage..."
    coverage run --source='.' manage.py test --parallel --settings=majobacore.settings.testing
    echo ""
    echo "📈 Reporte de coverage:"
    coverage report
    echo ""
    echo "💾 Reporte HTML generado en htmlcov/"
    coverage html
else
    echo "⚠️  Coverage no instalado, ejecutando tests sin coverage..."
    python manage.py test --parallel --settings=majobacore.settings.testing
fi

echo ""
echo "✅ Tests completados"
