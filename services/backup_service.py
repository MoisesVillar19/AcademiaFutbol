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


def listar_backups() -> list[dict]:
    """Lista backups con fecha UTC-5, tamaño y hash corto."""
    import hashlib
    destino = _resolver_ruta_backup()
    archivos = glob.glob(os.path.join(destino, "academia_*.db"))
    lista = []
    for f in sorted(archivos, key=lambda x: os.path.getmtime(x), reverse=True):
        try:
            st = os.stat(f)
            h = hashlib.sha256()
            with open(f, "rb") as fh:
                for chunk in iter(lambda: fh.read(8192), b""):
                    h.update(chunk)
            lista.append({"ruta": f, "fecha": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M (UTC-5)"), "tamano_mb": round(st.st_size/1024/1024,2), "hash": h.hexdigest()[:8]})
        except Exception:
            lista.append({"ruta": f, "fecha": "", "tamano_mb": 0, "hash": ""})
    return lista

def verificar_backup(ruta: str) -> tuple[bool, str]:
    """Verifica que el backup sea legible y no corrupto (cabecera SQLite)."""
    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master LIMIT 1")
        cur.fetchone()
        conn.close()
        return True, "Backup verificado correctamente"
    except Exception as e:
        return False, f"Backup corrupto: {e}"

def restaurar_backup(ruta: str, pin: str) -> tuple[bool, str]:
    """Restaura con PIN de emergencia, cierra conexión y copia."""
    from services import configuracion_service
    from utils.security import verify_password
    pin_hash = configuracion_service.obtener_valor("pin_emergencia")
    if not pin_hash or not verify_password(pin, pin_hash):
        return False, "PIN incorrecto"
    try:
        from database.connection import close_connection
        from database.restore import restore_backup
        close_connection()
        restore_backup(ruta)
        auditoria_service.registrar_log(auditoria_service.id_usuario_sesion(), "sistema", 0, "RESTORE", valor_nuevo=ruta)
        return True, "Restauración completada. Reinicie la app."
    except Exception as e:
        logger.error(f"Restore fallo: {e}")
        return False, str(e)

def rotar_backups(dias: int = 30) -> int:
    """Borra backups con más de N días, retorna cantidad borradas."""
    import time
    destino = _resolver_ruta_backup()
    archivos = glob.glob(os.path.join(destino, "academia_*.db"))
    borrados = 0
    limite = time.time() - dias*86400
    for f in archivos:
        try:
            if os.path.getmtime(f) < limite:
                os.remove(f)
                borrados += 1
        except Exception:
            pass
    if borrados:
        logger.info(f"Rotación backups: {borrados} borrados >{dias}d")
    return borrados

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
