from database.connection import get_connection, fetch_one, fetch_all
from models.tarifa import Tarifa
from utils.dates import get_now


def insertar(tarifa: Tarifa) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO tarifa
           (id_categoria, nombre, monto, descripcion, fecha_inicio, fecha_fin, observaciones, activo)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            tarifa.id_categoria,
            tarifa.nombre,
            tarifa.monto,
            tarifa.descripcion,
            tarifa.fecha_inicio,
            tarifa.fecha_fin,
            tarifa.observaciones,
            tarifa.activo,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_tarifa: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM tarifa WHERE id_tarifa = ?",
        (id_tarifa,),
    )


def obtener_por_categoria(id_categoria: int) -> list[dict]:
    return fetch_all(
        """SELECT t.*, c.nombre as categoria_nombre
           FROM tarifa t
           JOIN categoria c ON t.id_categoria = c.id_categoria
           WHERE t.id_categoria = ? AND t.activo = 1
           ORDER BY t.fecha_inicio DESC""",
        (id_categoria,),
    )


def obtener_activas() -> list[dict]:
    return fetch_all(
        """SELECT t.*, c.nombre as categoria_nombre
           FROM tarifa t
           JOIN categoria c ON t.id_categoria = c.id_categoria
           WHERE t.activo = 1
           ORDER BY c.nombre, t.nombre""",
    )


def actualizar(tarifa: Tarifa) -> None:
    conn = get_connection()
    conn.execute(
        """UPDATE tarifa SET
           id_categoria = ?, nombre = ?, monto = ?,
           descripcion = ?, fecha_inicio = ?, fecha_fin = ?,
           observaciones = ?, activo = ?
           WHERE id_tarifa = ?""",
        (
            tarifa.id_categoria,
            tarifa.nombre,
            tarifa.monto,
            tarifa.descripcion,
            tarifa.fecha_inicio,
            tarifa.fecha_fin,
            tarifa.observaciones,
            tarifa.activo,
            tarifa.id_tarifa,
        ),
    )
    conn.commit()


def soft_delete(id_tarifa: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE tarifa SET activo = 0 WHERE id_tarifa = ?",
        (id_tarifa,),
    )
    conn.commit()
