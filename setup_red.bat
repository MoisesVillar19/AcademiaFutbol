@echo off
setlocal
echo ========================================
echo  Configurar AcademiaFutbol en RED (BD unica compartida)
echo  Modelo A+C: las PCs abren el mismo archivo, sin copias
echo ========================================
echo.
cd /d "%~dp0"

if "%~1"=="" (
    echo Uso: setup_red "\\SERVIDOR\AcademiaDatos"
    echo.
    echo Ejemplo: setup_red "\\PC1\AcademiaDatos"
    echo (si ya existe una compartida con academia.db, use ESA, no cree otra)
    echo.
    set /p "SHARE=Escriba la ruta UNC del recurso compartido: "
) else (
    set "SHARE=%~1"
)
if "%SHARE%"=="" (
    echo [ERROR] Ruta vacia. Operacion cancelada.
    pause
    exit /b 1
)

echo.
echo [1/4] Verificando acceso al recurso: "%SHARE%"
if not exist "%SHARE%" (
    echo [ERROR] No se puede acceder. Verifique:
    echo   - PC servidor encendida y en la misma red
    echo   - Carpeta compartida con permiso total
    echo   - Regla firewall SMB (TCP/445) en el servidor
    echo   - Desde otra PC: dir "%SHARE%"
    echo.
    echo NO se creo ninguna BD local (anti-huerfana).
    pause
    exit /b 1
)
echo   OK acceso de lectura.

echo "%SHARE%\.write_test" >nul 2>&1
echo ok > "%SHARE%\.write_test" 2>nul
if errorlevel 1 (
    echo [ERROR] Sin permiso de ESCRITURA en el recurso. Pida permiso total.
    pause
    exit /b 1
)
del "%SHARE%\.write_test" >nul 2>&1
echo   OK permiso de escritura.

echo.
echo [2/4] Creando estructura central...
for %%D in (fotos comprobantes BackupsAcademia) do (
    if not exist "%SHARE%\%%D" mkdir "%SHARE%\%%D"
    echo   + %SHARE%\%%D
)

echo.
echo [3/4] Escribiendo config.ini (BD + backup + rutas centrales)...
py -c "import sys; p=r'%SHARE%'; open('config.ini','w',encoding='utf-8').write(f'[database]\npath={p}\\academia.db\n\n[backup]\ndir={p}\\BackupsAcademia\n\n[rutas]\nfotos={p}\\fotos\ncomprobantes={p}\\comprobantes\n')" 2>nul
if errorlevel 1 (
    echo [database] > config.ini
    echo path=%SHARE%\academia.db >> config.ini
    echo [backup] >> config.ini
    echo dir=%SHARE%\BackupsAcademia >> config.ini
)
type config.ini
echo.

echo [4/4] BD central...
if exist "%SHARE%\academia.db" (
    echo   OK ya existe, se conserva (el seed solo rellena lo faltante).
) else (
    echo   Se creara (con seed inicial) al primer arranque de la app.
)
echo.
echo ========================================
echo  Listo! Ejecute py main.py (o el .exe) en CADA PC con este mismo
echo  config.ini apuntando a "%SHARE%\academia.db".
echo  Copie este config.ini a las demas PCs (misma carpeta que el .exe).
echo ========================================
pause
