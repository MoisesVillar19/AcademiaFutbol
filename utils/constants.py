import os
import sys

# ── Detección de entorno ────────────────────────────────────────
_FROZEN = getattr(sys, "frozen", False)

if _FROZEN:
    # Ejecutable PyInstaller: rutas relativas al .exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    # Código fuente: rutas relativas al proyecto
    APP_DIR = os.path.dirname(os.path.dirname(__file__))

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) if not _FROZEN else os.path.join(os.path.dirname(sys.executable), "_internal")

# ── Versión ─────────────────────────────────────────────────────
def _leer_version() -> str:
    # En PyInstaller, VERSION está en _internal/
    if _FROZEN:
        version_file = os.path.join(BASE_DIR, "VERSION")
    else:
        version_file = os.path.join(APP_DIR, "VERSION")
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

__version__ = _leer_version()

# ── Base de datos ───────────────────────────────────────────────
# La BD siempre va al lado del .exe (fuera de _internal) para no borrarla al actualizar
DB_NAME = os.getenv("DB_NAME", "academia.db")
DB_PATH = os.path.join(APP_DIR, "database", DB_NAME)

ROLE_ADMIN = "ADMIN"
ROLE_SECRETARIA = "SECRETARIA"

STATUS_ACTIVO = "ACTIVO"
STATUS_RETIRADO = "RETIRADO"
STATUS_REINGRESANTE = "REINGRESANTE"

CUOTA_PENDIENTE = "PENDIENTE"
CUOTA_PARCIAL = "PARCIAL"
CUOTA_PAGADO = "PAGADO"
CUOTA_VENCIDO = "VENCIDO"

METODO_EFECTIVO = "EFECTIVO"
METODO_YAPE = "YAPE"
METODO_PLIN = "PLIN"
METODO_TRANSFERENCIA = "TRANSFERENCIA"

TIPO_BECA_PORCENTAJE = "PORCENTAJE"
TIPO_BECA_MONTO_FIJO = "MONTO_FIJO"

TIPO_MOVIMIENTO_ENTRADA = "ENTRADA"
TIPO_MOVIMIENTO_SALIDA = "SALIDA"
TIPO_MOVIMIENTO_AJUSTE = "AJUSTE"

TIPO_USO_CONSUMO_INTERNO = "CONSUMO_INTERNO"
TIPO_USO_VENTA = "VENTA"

CATEGORIA_INICIAL = [
    ("3-5", 3, 5),
    ("6-8", 6, 8),
    ("9-12", 9, 12),
    ("13-15", 13, 15),
    ("16-18", 16, 18),
]

CATEGORIA_PRODUCTO_INICIAL = [
    "INSUMO_DEPORTIVO",
    "INSUMO_ALIMENTO",
]

DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"


# ── Detección de OneDrive ──────────────────────────────────────
def detectar_onedrive() -> str | None:
    for var in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        ruta = os.environ.get(var)
        if ruta and os.path.isdir(ruta):
            return ruta
    ruta_fallback = os.path.join(os.path.expanduser("~"), "OneDrive")
    if os.path.isdir(ruta_fallback):
        return ruta_fallback
    return None


def _obtener_ruta_backup() -> str:
    ruta_onedrive = detectar_onedrive()
    if ruta_onedrive:
        return os.path.join(ruta_onedrive, "BackupsAcademia")
    return os.path.join(APP_DIR, "backups")


BACKUP_DIR = _obtener_ruta_backup()
