from database.connection import get_connection, fetch_one, fetch_all
from models.proveedor import Proveedor


def insertar(prov: Proveedor) -> int:
    conn = get_connection()
    cursor = conn.execute("INSERT INTO proveedor (nombre, telefono, activo) VALUES (?, ?, ?)", (prov.nombre, prov.telefono, prov.activo))
    conn.commit()
    return cursor.lastrowid

def obtener_todos(activo: int | None = 1) -> list[dict]:
    if activo is not None:
        return fetch_all("SELECT * FROM proveedor WHERE activo=? ORDER BY nombre", (activo,))
    return fetch_all("SELECT * FROM proveedor ORDER BY nombre")
