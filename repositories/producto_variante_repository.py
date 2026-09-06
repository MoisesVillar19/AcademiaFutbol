from database.connection import get_connection, fetch_one, fetch_all
from models.producto_variante import ProductoVariante


def insertar(var: ProductoVariante) -> int:
    conn = get_connection()
    cursor = conn.execute("INSERT INTO producto_variante (id_producto, id_talla, sku, codigo_barras, stock_minimo, activo) VALUES (?, ?, ?, ?, ?, ?)", (var.id_producto, var.id_talla, var.sku, var.codigo_barras, var.stock_minimo, var.activo))
    conn.commit()
    return cursor.lastrowid

def obtener_por_id(id_variante: int) -> dict | None:
    return fetch_one("SELECT pv.*, t.codigo as talla_codigo FROM producto_variante pv LEFT JOIN talla t ON pv.id_talla=t.id_talla WHERE pv.id_variante=?", (id_variante,))

def obtener_por_sku(sku: str) -> dict | None:
    return fetch_one("SELECT * FROM producto_variante WHERE sku=?", (sku,))

def obtener_por_producto(id_producto: int) -> list[dict]:
    return fetch_all("SELECT pv.*, t.codigo as talla_codigo FROM producto_variante pv LEFT JOIN talla t ON pv.id_talla=t.id_talla WHERE pv.id_producto=? AND pv.activo=1 ORDER BY t.codigo", (id_producto,))

def existe_sku(sku: str, exclude_id: int | None = None) -> bool:
    if exclude_id:
        return fetch_one("SELECT id_variante FROM producto_variante WHERE sku=? AND id_variante!=?", (sku, exclude_id)) is not None
    return fetch_one("SELECT id_variante FROM producto_variante WHERE sku=?", (sku,)) is not None
