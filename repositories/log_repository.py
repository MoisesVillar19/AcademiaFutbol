from database.connection import get_connection, fetch_one, fetch_all
from utils.dates import get_now


def insertar(id_usuario: int, tabla_afectada: str, id_registro: int,
             accion: str, valor_anterior: str = "", valor_nuevo: str = "") -> int:
    conn = get_connection()
    now = get_now()
    cursor = conn.execute(
        """INSERT INTO log
           (id_usuario, tabla_afectada, id_registro, accion, valor_anterior, valor_nuevo, fecha)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (id_usuario, tabla_afectada, id_registro, accion, valor_anterior, valor_nuevo, now),
    )
    conn.commit()
    return cursor.lastrowid


# Columnas extra: username (NULL si sistema/usuario borrado) + nombre.
# La vista muestra username o fallback "sistema (id=N)".
_JOIN_USUARIO = """
    LEFT JOIN usuario u ON u.id_usuario = log.id_usuario
    LEFT JOIN persona p ON p.id_persona = u.id_persona
"""
_COLS_USUARIO = """,
    u.username AS username,
    TRIM(COALESCE(p.nombres, '') || ' ' || COALESCE(p.apellidos, '')) AS usuario_nombre
"""


def obtener_todos(limit: int = 100, offset: int = 0) -> list[dict]:
    return fetch_all(
        "SELECT log.*" + _COLS_USUARIO + " FROM log" + _JOIN_USUARIO +
        " ORDER BY fecha DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )


def obtener_por_tabla(tabla_afectada: str, limit: int = 100) -> list[dict]:
    return fetch_all(
        "SELECT log.*" + _COLS_USUARIO + " FROM log" + _JOIN_USUARIO +
        " WHERE tabla_afectada = ? ORDER BY fecha DESC LIMIT ?",
        (tabla_afectada, limit),
    )


def obtener_por_usuario(id_usuario: int, limit: int = 100) -> list[dict]:
    return fetch_all(
        "SELECT log.*" + _COLS_USUARIO + " FROM log" + _JOIN_USUARIO +
        " WHERE log.id_usuario = ? ORDER BY fecha DESC LIMIT ?",
        (id_usuario, limit),
    )


def obtener_por_fecha(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    return fetch_all(
        "SELECT log.*" + _COLS_USUARIO + " FROM log" + _JOIN_USUARIO +
        " WHERE fecha BETWEEN ? AND ? ORDER BY fecha DESC",
        (fecha_inicio, fecha_fin),
    )


def contar_registros() -> int:
    row = fetch_one("SELECT COUNT(*) as total FROM log")
    return row["total"] if row else 0
