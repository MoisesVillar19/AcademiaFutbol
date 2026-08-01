from database.connection import get_connection, fetch_one, fetch_all
from models.movimiento_inventario import MovimientoInventario
from utils.dates import get_now


def insertar(movimiento: MovimientoInventario) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO movimiento_inventario
           (id_producto, id_usuario, tipo_movimiento, cantidad,
            stock_anterior, stock_nuevo, fecha_movimiento, motivo)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            movimiento.id_producto,
            movimiento.id_usuario,
            movimiento.tipo_movimiento,
            movimiento.cantidad,
            movimiento.stock_anterior,
            movimiento.stock_nuevo,
            movimiento.fecha_movimiento,
            movimiento.motivo,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_producto(id_producto: int) -> list[dict]:
    return fetch_all(
        """SELECT m.*, u.username
           FROM movimiento_inventario m
           JOIN usuario u ON m.id_usuario = u.id_usuario
           WHERE m.id_producto = ?
           ORDER BY m.fecha_movimiento DESC""",
        (id_producto,),
    )


def obtener_todos(limit: int = 100, offset: int = 0) -> list[dict]:
    return fetch_all(
        """SELECT m.*, u.username, p.nombre as producto_nombre, p.codigo
           FROM movimiento_inventario m
           JOIN usuario u ON m.id_usuario = u.id_usuario
           JOIN producto p ON m.id_producto = p.id_producto
           ORDER BY m.fecha_movimiento DESC
           LIMIT ? OFFSET ?""",
        (limit, offset),
    )


def obtener_por_fecha(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    return fetch_all(
        """SELECT m.*, u.username, p.nombre as producto_nombre, p.codigo
           FROM movimiento_inventario m
           JOIN usuario u ON m.id_usuario = u.id_usuario
           JOIN producto p ON m.id_producto = p.id_producto
           WHERE m.fecha_movimiento BETWEEN ? AND ?
           ORDER BY m.fecha_movimiento DESC""",
        (fecha_inicio, fecha_fin),
    )


def obtener_por_tipo(tipo_movimiento: str) -> list[dict]:
    return fetch_all(
        """SELECT m.*, u.username, p.nombre as producto_nombre, p.codigo
           FROM movimiento_inventario m
           JOIN usuario u ON m.id_usuario = u.id_usuario
           JOIN producto p ON m.id_producto = p.id_producto
           WHERE m.tipo_movimiento = ?
           ORDER BY m.fecha_movimiento DESC""",
        (tipo_movimiento,),
    )
