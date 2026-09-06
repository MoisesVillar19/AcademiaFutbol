@echo off
setlocal
echo ========================================
echo  Configurar AcademiaFutbol con OneDrive
echo  BD Central: OneDrive\Academia\academia.db
echo ========================================
echo.

cd /d "%~dp0"

REM -- 1. Detectar OneDrive --
set "ONEDRIVE_PATH="
if defined OneDrive if exist "%OneDrive%" set "ONEDRIVE_PATH=%OneDrive%"
if not defined ONEDRIVE_PATH if defined OneDriveConsumer if exist "%OneDriveConsumer%" set "ONEDRIVE_PATH=%OneDriveConsumer%"
if not defined ONEDRIVE_PATH if defined OneDriveCommercial if exist "%OneDriveCommercial%" set "ONEDRIVE_PATH=%OneDriveCommercial%"
if not defined ONEDRIVE_PATH if exist "%USERPROFILE%\OneDrive" set "ONEDRIVE_PATH=%USERPROFILE%\OneDrive%"
if not defined ONEDRIVE_PATH (
    echo [ERROR] No se encontro OneDrive.
    goto :local_fallback
)

echo [1/5] OneDrive detectado: "%ONEDRIVE_PATH%"
echo.

REM -- 2. Crear estructura central --
echo [2/5] Creando carpetas centrales...
if not exist "%ONEDRIVE_PATH%\Academia" mkdir "%ONEDRIVE_PATH%\Academia"
echo   + %ONEDRIVE_PATH%\Academia
if not exist "%ONEDRIVE_PATH%\Academia\fotos" mkdir "%ONEDRIVE_PATH%\Academia\fotos"
echo   + %ONEDRIVE_PATH%\Academia\fotos
if not exist "%ONEDRIVE_PATH%\Academia\comprobantes" mkdir "%ONEDRIVE_PATH%\Academia\comprobantes"
echo   + %ONEDRIVE_PATH%\Academia\comprobantes
if not exist "%ONEDRIVE_PATH%\BackupsAcademia" mkdir "%ONEDRIVE_PATH%\BackupsAcademia"
echo   + %ONEDRIVE_PATH%\BackupsAcademia
echo.

REM -- 3. Crear config.ini con Python (evita problemas de echo con [ ]) --
echo [3/5] Escribiendo config.ini...
py -c "import os; p=r'%ONEDRIVE_PATH%'; open('config.ini','w',encoding='utf-8').write(f'[database]\npath={p}\\Academia\\academia.db\n\n[backup]\ndir={p}\\BackupsAcademia\n\n[rutas]\nfotos={p}\\Academia\\fotos\ncomprobantes={p}\\Academia\\comprobantes\n')"
if errorlevel 1 (
    echo [ERROR] Python no encontrado, creando con echo...
    echo [database] > config.ini
    echo path=%ONEDRIVE_PATH%\Academia\academia.db >> config.ini
)
type config.ini
echo.

REM -- 4. Migrar BD local si existe --
set "LOCAL_DB=%~dp0database\academia.db"
set "CENTRAL_DB=%ONEDRIVE_PATH%\Academia\academia.db"
if exist "%LOCAL_DB%" (
    if not exist "%CENTRAL_DB%" (
        echo [4/5] Migrando BD local a OneDrive...
        copy /y "%LOCAL_DB%" "%CENTRAL_DB%" >nul
        echo   + copiado
    ) else (
        echo [4/5] BD central ya existe, se conserva.
    )
) else (
    echo [4/5] No hay BD local, se creara al iniciar la app.
)
echo.

REM -- 5. Verificar --
echo [5/5] Verificacion...
if exist "%CENTRAL_DB%" echo   OK BD central existe: %CENTRAL_DB%
if exist "config.ini" echo   OK config.ini creado
echo.
echo ========================================
echo  Listo! Ejecuta py main.py
echo ========================================
echo.
pause
exit /b 0

:local_fallback
echo [database] > config.ini
echo path=database\academia.db >> config.ini
echo Listo en modo local.
pause
exit /b 0
