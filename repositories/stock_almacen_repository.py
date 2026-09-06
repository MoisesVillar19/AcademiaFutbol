from database.connection import get_connection, fetch_one, fetch_all


def obtener(id_producto: int, id_variante: int | None, id_almacen: int, id_caja: int | None = None) -> dict | None:
    # Manejar NULL correctamente
    if id_variante is None and id_caja is None:
        return fetch_one("SELECT * FROM stock_almacen WHERE id_producto=? AND id_variante IS NULL AND id_almacen=? AND id_caja IS NULL", (id_producto, id_almacen))
    # fallback genérico: buscar por combinacion
    sql = "SELECT * FROM stock_almacen WHERE id_producto=? AND id_almacen=?"
    params=[id_producto, id_almacen]
    if id_variante is None:
        sql += " AND id_variante IS NULL"
    else:
        sql += " AND id_variante=?"
        params.append(id_variante)
    if id_caja is None:
        sql += " AND id_caja IS NULL"
    else:
        sql += " AND id_caja=?"
        params.append(id_caja)
    return fetch_one(sql, tuple(params))

def upsert_stock(id_producto: int, id_variante: int | None, id_almacen: int, id_caja: int | None, delta: int) -> int:
    """Incrementa/decrementa stock y retorna nuevo stock. Crea fila si no existe."""
    conn = get_connection()
    row = obtener(id_producto, id_variante, id_almacen, id_caja)
    if row:
        nuevo = (row["stock"] or 0) + delta
        conn.execute("UPDATE stock_almacen SET stock=? WHERE id_stock=?", (nuevo, row["id_stock"]))
        conn.commit()
        return nuevo
    else:
        nuevo = delta
        conn.execute("INSERT INTO stock_almacen (id_producto, id_variante, id_almacen, id_caja, stock) VALUES (?, ?, ?, ?, ?)", (id_producto, id_variante, id_almacen, id_caja, nuevo))
        conn.commit()
        return nuevo

def obtener_por_producto(id_producto: int) -> list[dict]:
    return fetch_all("SELECT sa.*, a.nombre as almacen_nombre, c.nombre as caja_nombre FROM stock_almacen sa JOIN almacen a ON sa.id_almacen=a.id_almacen LEFT JOIN caja c ON sa.id_caja=c.id_caja WHERE sa.id_producto=?", (id_producto,))

def obtener_bajo_stock_por_almacen(id_almacen: int | None = None) -> list[dict]:
    sql = "SELECT p.codigo, p.nombre, sa.stock, pv.stock_minimo as minimo_variante, p.stock_minimo as minimo_prod FROM stock_almacen sa JOIN producto p ON sa.id_producto=p.id_producto LEFT JOIN producto_variante pv ON sa.id_variante=pv.id_variante WHERE sa.stock <= COALESCE(pv.stock_minimo, p.stock_minimo)"
    params=[]
    if id_almacen is not None:
        sql += " AND sa.id_almacen=?"
        params.append(id_almacen)
    return fetch_all(sql, tuple(params))
