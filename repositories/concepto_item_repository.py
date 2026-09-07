from database.connection import fetch_all, get_connection


def obtener_por_concepto(id_concepto: int) -> list[dict]:
    return fetch_all(
        "SELECT ci.*, p.nombre as producto_nombre, p.codigo, p.precio_venta FROM concepto_item ci JOIN producto p ON p.id_producto=ci.id_producto WHERE ci.id_concepto=?",
        (id_concepto,),
    )


def reemplazar_items(id_concepto: int, items: list[dict]) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM concepto_item WHERE id_concepto=?", (id_concepto,))
    for it in items:
        conn.execute(
            "INSERT INTO concepto_item (id_concepto, id_producto, cantidad) VALUES (?, ?, ?)",
            (id_concepto, it["id_producto"], int(it.get("cantidad", 1))),
        )
    conn.commit()


def insertar(id_concepto: int, id_producto: int, cantidad: int = 1) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO concepto_item (id_concepto, id_producto, cantidad) VALUES (?, ?, ?)",
        (id_concepto, id_producto, cantidad),
    )
    conn.commit()
    return cur.lastrowid
