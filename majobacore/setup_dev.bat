@echo off
echo ========================================
echo   MajobaSyS - Development Setup
echo ========================================
echo.

REM Verificar si existe entorno virtual
if not exist "..\venv" (
    echo [1/7] Creando entorno virtual...
    python -m venv ..\venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: No se pudo crear el entorno virtual.
        echo Verifica que Python este instalado.
        pause
        exit /b 1
    )
) else (
    echo [1/7] Entorno virtual ya existe. Saltando...
)

echo [2/7] Activando entorno virtual...
call ..\venv\Scripts\activate.bat

echo [3/7] Actualizando pip...
python -m pip install --upgrade pip

echo [4/7] Instalando dependencias de desarrollo...
pip install -r requirements\development.txt

echo [5/7] Verificando archivo .env...
if not exist ".env" (
    echo Archivo .env no encontrado.
    if exist ".env.example" (
        echo Copiando desde .env.example...
        copy .env.example .env
        echo.
        echo IMPORTANTE: Edita el archivo .env y configura:
        echo   - SECRET_KEY (genera una con: python manage.py generate_secret_key)
        echo   - EMAIL settings si es necesario
        echo.
    ) else (
        echo ERROR: No existe .env ni .env.example
        echo Crea manualmente un archivo .env basado en la documentacion.
    )
) else (
    echo Archivo .env ya existe.
)

echo [6/7] Aplicando migraciones...
python manage.py migrate --settings=majobacore.settings.development

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migraciones fallaron.
    pause
    exit /b 1
)

echo [7/7] Verificando directorios necesarios...
if not exist "logs" mkdir logs
if not exist "media" mkdir media

echo.
echo ========================================
echo   Setup completado exitosamente!
echo ========================================
echo.
echo Proximos pasos:
echo   1. Edita el archivo .env si es necesario
echo   2. Crea un superusuario: python manage.py createsuperuser
echo   3. Ejecuta el servidor: run_dev.bat
echo.
echo ========================================
pause
