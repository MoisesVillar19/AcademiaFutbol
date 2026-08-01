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


def obtener_todos(limit: int = 100, offset: int = 0) -> list[dict]:
    return fetch_all(
        "SELECT * FROM log ORDER BY fecha DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )


def obtener_por_tabla(tabla_afectada: str, limit: int = 100) -> list[dict]:
    return fetch_all(
        "SELECT * FROM log WHERE tabla_afectada = ? ORDER BY fecha DESC LIMIT ?",
        (tabla_afectada, limit),
    )


def obtener_por_usuario(id_usuario: int, limit: int = 100) -> list[dict]:
    return fetch_all(
        "SELECT * FROM log WHERE id_usuario = ? ORDER BY fecha DESC LIMIT ?",
        (id_usuario, limit),
    )


def obtener_por_fecha(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    return fetch_all(
        "SELECT * FROM log WHERE fecha BETWEEN ? AND ? ORDER BY fecha DESC",
        (fecha_inicio, fecha_fin),
    )


def contar_registros() -> int:
    row = fetch_one("SELECT COUNT(*) as total FROM log")
    return row["total"] if row else 0
