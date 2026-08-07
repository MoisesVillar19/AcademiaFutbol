@echo off
echo ========================================
echo  Construyendo AcademiaFutbol con PyInstaller
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Limpiando build anterior...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo [2/3] Ejecutando PyInstaller...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean AcademiaFutbol.spec
if errorlevel 1 (
    echo.
    echo ERROR: Fallo la construccion con PyInstaller.
    pause
    exit /b 1
)

echo [3/3] Copiando assets necesarios...
if not exist "dist\AcademiaFutbol\assets\images" mkdir "dist\AcademiaFutbol\assets\images"
copy /y "assets\images\logo_roncalli.png" "dist\AcademiaFutbol\assets\images\" >nul 2>&1

echo.
echo ========================================
echo  Construccion completada!
echo  Ubicacion: dist\AcademiaFutbol\
echo ========================================
echo.
echo Para probar la app, ejecuta:
echo   dist\AcademiaFutbol\AcademiaFutbol.exe
echo.
pause
