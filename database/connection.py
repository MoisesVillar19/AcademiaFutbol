import sqlite3
import os
from contextlib import contextmanager
from utils.constants import DB_PATH
from utils.logger import logger


_nivel_transaccion: int = 0

BUSY_TIMEOUT_MS = 20000


class ConexionConTransaccion(sqlite3.Connection):
    """Conexion que pospone los commits individuales mientras haya una transaccion activa."""

    def commit(self):
        if _nivel_transaccion == 0:
            super().commit()


_connection: sqlite3.Connection | None = None


def es_ruta_red(path: str | None = None) -> bool:
    """True si la BD vive en red (UNC \\\\servidor\\...). En red se evita WAL."""
    p = os.path.abspath(path or DB_PATH)
    if p.startswith("\\\\") or p.startswith("//"):
        return True
    # Unidad mapeada a red (Windows): GetDriveTypeW == DRIVE_REMOTE (4)
    try:
        import ctypes
        raiz = os.path.splitdrive(p)[0] + "\\"
        if raiz and raiz != "\\":
            if ctypes.windll.kernel32.GetDriveTypeW(raiz) == 4:
                return True
    except Exception:
        pass
    return False


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        dirname = os.path.dirname(DB_PATH)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        _connection = sqlite3.connect(DB_PATH, factory=ConexionConTransaccion,
                                      timeout=BUSY_TIMEOUT_MS / 1000)
        _connection.row_factory = sqlite3.Row
        # WAL prohibido sobre red (SMB): rollback journal en red, WAL en local
        try:
            if es_ruta_red():
                _connection.execute("PRAGMA journal_mode=DELETE")
            else:
                _connection.execute("PRAGMA journal_mode=WAL")
        except Exception as e:
            logger.warning(f"No se pudo fijar journal_mode: {e}")
        _connection.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection


def close_connection() -> None:
    global _connection
    global _nivel_transaccion
    if _connection is not None:
        _connection.close()
        _connection = None
    _nivel_transaccion = 0


def estado_bd(path: str | None = None) -> dict:
    """Diagnóstico para UI: ruta, si es red, accesible, journal y tamaño."""
    crudo = path or DB_PATH
    if crudo == ":memory:":
        return {"ruta": ":memory:", "es_red": False, "existe": True,
                "accesible": True, "journal": "memory", "bytes": 0}
    ruta = os.path.abspath(crudo)
    info: dict = {"ruta": ruta, "es_red": es_ruta_red(ruta),
                  "existe": os.path.isfile(ruta), "accesible": False,
                  "journal": "?", "bytes": 0}
    try:
        info["bytes"] = os.path.getsize(ruta)
    except Exception:
        pass
    if info["es_red"] and not os.path.isdir(os.path.dirname(ruta)):
        return info
    try:
        conn = sqlite3.connect(ruta, timeout=5)
        try:
            conn.execute("SELECT 1")
            jm = conn.execute("PRAGMA journal_mode").fetchone()
            info["journal"] = jm[0] if jm else "?"
            info["accesible"] = True
        finally:
            conn.close()
    except Exception:
        pass
    return info


def cerrar_limpio(checkpoint: bool = True) -> None:
    """Apagado seguro: vacía el WAL local al .db y cierra. Evita -wal
    huérfanos y locks que impiden reabrir (local y red)."""
    global _connection
    try:
        if _connection is not None and checkpoint and not es_ruta_red():
            try:
                _connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except Exception:
                pass
    finally:
        close_connection()


@contextmanager
def transaccion():
    """Agrupa escrituras en una sola transaccion atomica.

    Los commits de repositorios dentro del bloque se posponen hasta salir;
    si ocurre una excepcion se hace rollback de todo el bloque.
    Concurrencia en red: la espera ante locks la maneja SQLite con
    busy_timeout (20s); no se reintenta el cuerpo aquí (un generador
    contextmanager no puede re-ejecutar el bloque with).
    """
    global _nivel_transaccion
    conn = get_connection()
    _nivel_transaccion += 1
    try:
        yield conn
        _nivel_transaccion -= 1
        if _nivel_transaccion == 0:
            conn.commit()
    except Exception:
        _nivel_transaccion -= 1
        if _nivel_transaccion <= 0:
            _nivel_transaccion = 0
        conn.rollback()
        raise


def execute_query(sql: str, params: tuple = ()) -> sqlite3.Cursor:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return cursor


def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return [dict(row) for row in cursor.fetchall()]
