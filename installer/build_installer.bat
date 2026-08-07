@echo off
echo ========================================
echo  Construyendo Instalador con Inno Setup
echo ========================================
echo.

cd /d "%~dp0"

REM Buscar Inno Setup en las rutas comunes
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 7\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 7\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 7\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 7\ISCC.exe"
)

if "%ISCC%"=="" (
    echo ERROR: No se encontro Inno Setup.
    echo Instala Inno Setup 6 desde: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

echo Inno Setup encontrado: %ISCC%
echo.

REM Verificar que exista la carpeta de PyInstaller
if not exist "..\dist\AcademiaFutbol\AcademiaFutbol.exe" (
    echo ERROR: No se encontro el ejecutable compilado.
    echo Ejecuta primero: build.bat
    pause
    exit /b 1
)

echo [1/2] Compilando instalador...
"%ISCC%" setup.iss
if errorlevel 1 (
    echo.
    echo ERROR: Fallo la compilacion del instalador.
    pause
    exit /b 1
)

echo [2/2] Instalador generado correctamente!
echo.
echo ========================================
echo  Instalador generado!
echo  Ubicacion: installer\Output\
echo ========================================
echo.
echo Para instalar en otra PC:
echo   1. Copia el archivo .exe de installer\Output\
echo   2. Ejecutalo en la PC destino
echo   3. Sigue el wizard de instalacion
echo.
pause
