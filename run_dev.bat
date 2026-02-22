@echo off
echo ========================================
echo   MajobaSyS - Development Server
echo ========================================
echo.

REM Verificar si existe entorno virtual
if not exist "..\venv\Scripts\activate.bat" (
    echo ERROR: Entorno virtual no encontrado.
    echo Ejecute setup_dev.bat primero.
    pause
    exit /b 1
)

echo [1/3] Activando entorno virtual...
call ..\venv\Scripts\activate.bat

echo [2/3] Verificando migraciones pendientes...
python manage.py makemigrations --check --dry-run --settings=majobacore.settings.development

echo [3/3] Ejecutando checks de Django...
python manage.py check --settings=majobacore.settings.development

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Django check falló. Revise los errores arriba.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Servidor iniciando...
echo   URL: http://127.0.0.1:8000
echo   Admin: http://127.0.0.1:8000/admin
echo   Manager: http://127.0.0.1:8000/manager
echo ========================================
echo   Presione Ctrl+C para detener
echo ========================================
echo.

python manage.py runserver --settings=majobacore.settings.development
