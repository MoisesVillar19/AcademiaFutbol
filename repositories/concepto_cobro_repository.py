from database.connection import fetch_all, fetch_one, get_connection
from utils.dates import get_now


def obtener_todos(activo: int | None = 1) -> list[dict]:
    if activo is not None:
        return fetch_all("SELECT * FROM concepto_cobro WHERE activo=? ORDER BY nombre", (activo,))
    return fetch_all("SELECT * FROM concepto_cobro ORDER BY nombre")


def obtener_por_id(id_concepto: int) -> dict | None:
    return fetch_one("SELECT * FROM concepto_cobro WHERE id_concepto=?", (id_concepto,))


def insertar(data: dict) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO concepto_cobro (nombre, tipo, monto, descripcion, activo) VALUES (?, ?, ?, ?, ?)",
        (data["nombre"], data["tipo"], data["monto"], data.get("descripcion", ""), data.get("activo", 1)),
    )
    conn.commit()
    return cur.lastrowid


def actualizar(id_concepto: int, data: dict) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE concepto_cobro SET nombre=?, tipo=?, monto=?, descripcion=? WHERE id_concepto=?",
        (data["nombre"], data["tipo"], data["monto"], data.get("descripcion", ""), id_concepto),
    )
    conn.commit()


def soft_delete(id_concepto: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE concepto_cobro SET activo=0 WHERE id_concepto=?", (id_concepto,))
    conn.commit()


def activar(id_concepto: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE concepto_cobro SET activo=1 WHERE id_concepto=?", (id_concepto,))
    conn.commit()
