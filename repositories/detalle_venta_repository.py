from database.connection import get_connection, fetch_all
from models.detalle_venta import DetalleVenta


def insertar(detalle: DetalleVenta) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
        (detalle.id_venta, detalle.id_producto, detalle.cantidad, detalle.precio_unitario, detalle.subtotal),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_venta(id_venta: int) -> list[dict]:
    return fetch_all(
        """SELECT dv.*, p.nombre as producto_nombre, p.codigo
           FROM detalle_venta dv JOIN producto p ON dv.id_producto = p.id_producto
           WHERE dv.id_venta = ?""",
        (id_venta,),
    )
