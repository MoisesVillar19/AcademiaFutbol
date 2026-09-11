AcademiaFutbol v1.0.3 - Si Windows bloquea el instalador/EXE
===============================================================================
LEEME PRIMERO: docs/despliegue/guia_instalacion.md (paso a paso con dibujos de texto)

ESTE EXE ES LEGITIMO (PyInstaller + CustomTkinter). Sin firma de codigo de pago,
Windows muestra "Editor desconocido" / "Windows protegió su PC". NO ES VIRUS.
(PyInstaller + bcrypt a veces da falso positivo Trojan:Win32/Wacatac.)

ELIGE TU CASO (A, B, C o D):

[A] SmartScreen AZUL "Windows protegió su PC" (más común)
    1. Clic en "Más información"
    2. Clic en "Ejecutar de todas formas"
    3. Sigue wizard normal (6 pasos)

[B] Archivo bloqueado "No se puede ejecutar" / Zone.Identifier
    - Gráfico: clic derecho .exe -> Propiedades -> marcar "Desbloquear" -> Aplicar
    - PowerShell (recomendado):
      Unblock-File -Path ".\AcademiaFutbol-Setup-1.0.3.exe"
      Unblock-File -Path ".\AcademiaFutbol-v1.0.3.zip"  (si usas ZIP)

[C] Defender/Antivirus lo borra ("Amenaza encontrada")
    1. Seguridad de Windows -> Protección antivirus -> Historial -> Permitir
    2. Agregar exclusión permanente:
       Seguridad de Windows -> Administrar configuración -> Exclusiones
       -> Agregar Carpeta -> C:\Program Files\AcademiaFutbol\
       (o la carpeta donde extrajiste el ZIP, ej C:\AcademiaFutbol\)
    3. Volver a descargar/extraer si lo puso en cuarentena
    - Verificación SHA256 (hash del Release v1.0.3):
      certutil -hashfile AcademiaFutbol-Setup-1.0.3.exe SHA256
        -> 9dd7c5403671f03e66b6cd6c37559c9212268489aaa60fdd365b57945591e5c0
      certutil -hashfile AcademiaFutbol-v1.0.3.zip SHA256
        -> compara con SHA256-v1.0.3.txt del Release

[D] Sin permiso de admin / PC bloqueada
    -> USA EL ZIP PORTABLE (no pide permisos, ya viene parchado: escribe en
       LOCALAPPDATA, no necesita admin):
    1. Unblock-File AcademiaFutbol-v1.0.3.zip (desbloquear ZIP primero!)
    2. Clic derecho ZIP -> Extraer todo... -> C:\AcademiaFutbol\
       (mantener _internal\ y AcademiaFutbol.exe juntos)
    3. Ejecuta setup_red.bat (incluido) para conectar a \\SERVIDOR\Academia
    4. Doble clic AcademiaFutbol.exe -> crear acceso directo al Escritorio

RED (4 PCs, una sola BD):
    - NO copies academia.db entre PCs. Ejecuta setup_red.bat en cada PC.
    - "No se puede acceder a la base de datos" = enciende la PC principal.
    - Probar conexión: Configuración -> Respaldo -> Probar conexión.

Actualizaciones:
    - Barra con %, MB/s y ETA. En Program Files pedirá UAC (normal).
    - Manual: Configuración -> Actualizaciones -> Buscar ahora.
