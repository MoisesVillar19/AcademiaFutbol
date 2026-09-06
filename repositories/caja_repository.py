from database.connection import get_connection, fetch_one, fetch_all
from models.caja import Caja


def insertar(caja: Caja) -> int:
    conn = get_connection()
    cursor = conn.execute("INSERT INTO caja (id_almacen, nombre, responsable, activo) VALUES (?, ?, ?, ?)", (caja.id_almacen, caja.nombre, caja.responsable, caja.activo))
    conn.commit()
    return cursor.lastrowid

def obtener_por_id(id_caja: int) -> dict | None:
    return fetch_one("SELECT * FROM caja WHERE id_caja = ?", (id_caja,))

def obtener_todos(id_almacen: int | None = None, activo: int | None = 1) -> list[dict]:
    sql = "SELECT c.*, a.nombre as almacen_nombre FROM caja c JOIN almacen a ON c.id_almacen=a.id_almacen WHERE 1=1"
    params=[]
    if id_almacen is not None:
        sql += " AND c.id_almacen=?"
        params.append(id_almacen)
    if activo is not None:
        sql += " AND c.activo=?"
        params.append(activo)
    sql += " ORDER BY a.nombre, c.nombre"
    return fetch_all(sql, tuple(params))
