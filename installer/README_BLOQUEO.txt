AcademiaFutbol - Si Windows bloquea el instalador/EXE (sin firma, cualquier PC)
===============================================================================
Fecha: 2026-09-07 | Versión: v1.0.2 | Alternativa ZIP incluida

ESTE EXE ES LEGITIMO (PyInstaller + CustomTkinter). Sin dinero para firma de codigo,
Windows muestra "Editor desconocido" / "Windows protegió su PC". NO ES VIRUS.
PyInstaller + bcrypt a veces da falso positivo Trojan:Win32/Wacatac.

ELIGE TU CASO (A, B, C o D):

[A] SmartScreen AZUL "Windows protegió su PC" (más común)
    1. Clic en "Más información"
    2. Clic en "Ejecutar de todas formas"
    3. Sigue wizard normal (6 pasos)

[B] Archivo bloqueado "No se puede ejecutar" / Zone.Identifier
    - Gráfico: clic derecho .exe -> Propiedades -> marcar "Desbloquear" -> Aplicar
    - PowerShell (recomendado):
      Unblock-File -Path ".\AcademiaFutbol-Setup-1.0.2.exe"
      Unblock-File -Path ".\AcademiaFutbol-v1.0.2.zip"  (si usas ZIP)
      # verificar/fix ADS:
      Remove-Item -Path ".\AcademiaFutbol-Setup-1.0.2.exe:Zone.Identifier" -ErrorAction SilentlyContinue

[C] Defender/Antivirus lo borra ("Amenaza encontrada")
    1. Seguridad de Windows -> Protección antivirus -> Historial -> Permitir
    2. Agregar exclusión permanente:
       Seguridad de Windows -> Administrar configuración -> Exclusiones
       -> Agregar Carpeta -> C:\Program Files\AcademiaFutbol\
       (o la carpeta donde extrajiste el ZIP, ej C:\AcademiaFutbol\)
    3. Volver a descargar/extraer si lo puso en cuarentena
    - Verificación SHA256 (hash del Release v1.0.2, copy/paste):
      certutil -hashfile AcademiaFutbol-Setup-1.0.2.exe SHA256
      certutil -hashfile AcademiaFutbol-v1.0.2.zip SHA256
      Debe coincidir con el publicado en GitHub Releases v1.0.2.

[D] Sin permiso de admin / no puedes instalar en C:\Program Files\ (PC bloqueada, cabina)
    -> NO USES EL SETUP, USA EL ZIP PORTABLE (no pide permisos):
    1. Unblock-File AcademiaFutbol-v1.0.2.zip (desbloquear ZIP primero!)
    2. Clic derecho ZIP -> Extraer todo... -> C:\AcademiaFutbol\  (o Documentos\AcademiaFutbol\)
       (mantener _internal\ y AcademiaFutbol.exe juntos)
    3. Doble clic AcademiaFutbol.exe -> funciona igual (BD sigue en OneDrive\Academia\academia.db)
    4. Crear acceso directo: clic derecho AcademiaFutbol.exe -> Crear acceso directo -> Escritorio
    Esta es la opción oficial para cualquier PC sin OneDrive/admin.

Logs si da PermissionError (fix v1.0.1):
  - Antes v1.0.0: C:\Program Files\_internal\logs -> Acceso denegado
  - Ahora v1.0.1+: OneDrive\Academia\logs\academia.log  o  %LOCALAPPDATA%\AcademiaFutbol\logs\academia.log
    (automático, no necesitas admin)

Actualizaciones v1.0.2 (dual Setup/ZIP):
  - Si instalaste con Setup en Program Files: actualizará con Setup silencioso (pedirá UAC, es normal).
  - Si instalaste portable ZIP: actualiza con ZIP sin permisos (MB/s, ETA visible).
  - Botón manual: Configuración -> Actualizaciones -> Buscar actualizaciones ahora.

Soporte: docs/despliegue/instalacion.md §2.1 y §10 | manual_sistema.md
Hashes SHA256 del Release v1.0.2:
  (ver GitHub Releases v1.0.2 notas o ejecutar certutil arriba)
