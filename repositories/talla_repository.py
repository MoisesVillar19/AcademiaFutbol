from database.connection import get_connection, fetch_one, fetch_all
from models.talla import Talla


def insertar(talla: Talla) -> int:
    conn = get_connection()
    cursor = conn.execute("INSERT INTO talla (codigo, descripcion, activo) VALUES (?, ?, ?)", (talla.codigo, talla.descripcion, talla.activo))
    conn.commit()
    return cursor.lastrowid

def obtener_por_id(id_talla: int) -> dict | None:
    return fetch_one("SELECT * FROM talla WHERE id_talla = ?", (id_talla,))

def obtener_por_codigo(codigo: str) -> dict | None:
    return fetch_one("SELECT * FROM talla WHERE codigo = ?", (codigo,))

def obtener_todas(activo: int | None = 1) -> list[dict]:
    if activo is not None:
        return fetch_all("SELECT * FROM talla WHERE activo = ? ORDER BY codigo", (activo,))
    return fetch_all("SELECT * FROM talla ORDER BY codigo")

def actualizar(talla: Talla) -> None:
    conn = get_connection()
    conn.execute("UPDATE talla SET codigo=?, descripcion=?, activo=? WHERE id_talla=?", (talla.codigo, talla.descripcion, talla.activo, talla.id_talla))
    conn.commit()

def soft_delete(id_talla: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE talla SET activo=0 WHERE id_talla=?", (id_talla,))
    conn.commit()
