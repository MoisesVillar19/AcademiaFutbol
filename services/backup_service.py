import glob
import os
from datetime import datetime

from database.backup import create_backup
from services import auditoria_service, configuracion_service
from utils.logger import logger


def _resolver_ruta_backup() -> str:
    """Resuelve la carpeta de respaldos desde CONFIGURACION.ruta_backup (RN-029).

    Rutas relativas se interpretan respecto al directorio de la aplicacion.
    Si no hay configuracion, usa la carpeta detectada por defecto.
    """
    from utils.constants import APP_DIR, BACKUP_DIR
    ruta = configuracion_service.obtener_valor("ruta_backup")
    if not ruta or not str(ruta).strip():
        return BACKUP_DIR
    ruta = str(ruta).strip()
    if not os.path.isabs(ruta):
        ruta = os.path.join(APP_DIR, ruta)
    return ruta


def crear_backup(id_usuario: int | None = None) -> tuple[bool, str, str | None]:
    """Crea un respaldo de la BD y lo registra en auditoria (RN-030)."""
    try:
        destino = _resolver_ruta_backup()
        ruta_respaldo = create_backup(custom_path=destino)
    except Exception as e:
        logger.error(f"Error al crear backup: {e}")
        return False, f"Error al crear el respaldo: {e}", None

    auditoria_service.registrar_log(
        id_usuario=id_usuario or auditoria_service.id_usuario_sesion(),
        tabla_afectada="sistema",
        id_registro=0,
        accion="BACKUP",
        valor_nuevo=ruta_respaldo,
    )
    logger.info(f"Backup creado: {ruta_respaldo}")
    return True, "Respaldo creado correctamente", ruta_respaldo


def dias_desde_ultimo_backup() -> float | None:
    """Dias transcurridos desde el respaldo mas reciente (None si nunca hubo)."""
    destino = _resolver_ruta_backup()
    archivos = glob.glob(os.path.join(destino, "academia_*.db"))
    if not archivos:
        return None
    ultimo_mtime = max(os.path.getmtime(a) for a in archivos)
    delta = datetime.now() - datetime.fromtimestamp(ultimo_mtime)
    return delta.total_seconds() / 86400


def verificar_backup_automatico() -> tuple[bool, str]:
    """Respeta CONFIGURACION.backup_automatico y frecuencia_backup (RN-030).

    Retorna (True, msg) solo cuando se creo un respaldo nuevo.
    """
    config = configuracion_service.obtener_configuracion() or {}
    if not config.get("backup_automatico", 0):
        return False, "Backup automático deshabilitado"

    try:
        frecuencia = max(int(config.get("frecuencia_backup", 7) or 7), 1)
    except (ValueError, TypeError):
        frecuencia = 7

    dias = dias_desde_ultimo_backup()
    if dias is not None and dias < frecuencia:
        return False, f"Último respaldo hace {dias:.1f} días (frecuencia: {frecuencia})"

    exito, msg, _ = crear_backup()
    return exito, msg
