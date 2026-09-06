from database.connection import get_connection, fetch_one, fetch_all
from models.almacen import Almacen


def insertar(almacen: Almacen) -> int:
    conn = get_connection()
    cursor = conn.execute("INSERT INTO almacen (nombre, direccion, activo) VALUES (?, ?, ?)", (almacen.nombre, almacen.direccion, almacen.activo))
    conn.commit()
    return cursor.lastrowid

def obtener_por_id(id_almacen: int) -> dict | None:
    return fetch_one("SELECT * FROM almacen WHERE id_almacen = ?", (id_almacen,))

def obtener_por_nombre(nombre: str) -> dict | None:
    return fetch_one("SELECT * FROM almacen WHERE nombre = ?", (nombre,))

def obtener_todos(activo: int | None = 1) -> list[dict]:
    if activo is not None:
        return fetch_all("SELECT * FROM almacen WHERE activo = ? ORDER BY nombre", (activo,))
    return fetch_all("SELECT * FROM almacen ORDER BY nombre")

def obtener_todos_count() -> int:
    row = fetch_one("SELECT COUNT(*) as total FROM almacen WHERE activo=1")
    return row["total"] if row else 0
