from database.connection import get_connection, fetch_one, fetch_all
from models.lote import Lote


def insertar(lote: Lote) -> int:
    conn = get_connection()
    cursor = conn.execute("INSERT INTO lote (id_producto, id_variante, id_almacen, codigo_lote, fecha_ingreso, fecha_caducidad, id_proveedor, cantidad, stock_restante) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (lote.id_producto, lote.id_variante, lote.id_almacen, lote.codigo_lote, lote.fecha_ingreso, lote.fecha_caducidad, lote.id_proveedor, lote.cantidad, lote.stock_restante))
    conn.commit()
    return cursor.lastrowid

def obtener_vigentes(id_producto: int | None = None) -> list[dict]:
    sql = "SELECT * FROM lote WHERE stock_restante > 0 AND (fecha_caducidad IS NULL OR fecha_caducidad >= date('now'))"
    params=[]
    if id_producto is not None:
        sql += " AND id_producto=?"
        params.append(id_producto)
    sql += " ORDER BY fecha_caducidad ASC, fecha_ingreso ASC"
    return fetch_all(sql, tuple(params))

def obtener_por_vencer(dias: int = 30) -> list[dict]:
    return fetch_all("SELECT l.*, p.nombre as producto_nombre FROM lote l JOIN producto p ON l.id_producto=p.id_producto WHERE l.stock_restante>0 AND l.fecha_caducidad IS NOT NULL AND date(l.fecha_caducidad) BETWEEN date('now') AND date('now', '+'||?||' days') ORDER BY l.fecha_caducidad", (dias,))

def descontar_fifo(id_producto: int, id_variante: int | None, id_almacen: int, cantidad: int) -> list[dict]:
    """Descuenta FIFO por caducidad, retorna lotes afectados."""
    lotes = obtener_vigentes(id_producto)
    # filtrar por variante/almacen si corresponde
    filtrados = [l for l in lotes if (id_variante is None or l["id_variante"]==id_variante) and l["id_almacen"]==id_almacen]
    if not filtrados:
        # si no hay lotes, no descontar lote (venta de no perecible)
        return []
    restante = cantidad
    usados=[]
    conn = get_connection()
    for lote in filtrados:
        if restante <=0:
            break
        tomar = min(lote["stock_restante"], restante)
        conn.execute("UPDATE lote SET stock_restante = stock_restante - ? WHERE id_lote=?", (tomar, lote["id_lote"]))
        usados.append({"id_lote": lote["id_lote"], "cantidad": tomar})
        restante -= tomar
    conn.commit()
    if restante >0:
        # No hay suficiente en lotes, pero se descuenta igual de stock general (para no bloquear venta de no perecible sin lote)
        pass
    return usados
