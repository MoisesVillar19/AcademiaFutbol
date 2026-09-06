from database.connection import get_connection, fetch_one, fetch_all
from models.tipo_uniforme import TipoUniforme


def insertar(tipo: TipoUniforme) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tipo_uniforme (nombre, descripcion, activo) VALUES (?, ?, ?)",
        (tipo.nombre, tipo.descripcion, tipo.activo),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_tipo: int) -> dict | None:
    return fetch_one("SELECT * FROM tipo_uniforme WHERE id_tipo_uniforme = ?", (id_tipo,))


def obtener_por_nombre(nombre: str) -> dict | None:
    return fetch_one("SELECT * FROM tipo_uniforme WHERE nombre = ?", (nombre,))


def obtener_todos(activo: int | None = None) -> list[dict]:
    if activo is not None:
        return fetch_all("SELECT * FROM tipo_uniforme WHERE activo = ? ORDER BY nombre", (activo,))
    return fetch_all("SELECT * FROM tipo_uniforme ORDER BY nombre")


def actualizar(tipo: TipoUniforme) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE tipo_uniforme SET nombre = ?, descripcion = ?, activo = ? WHERE id_tipo_uniforme = ?",
        (tipo.nombre, tipo.descripcion, tipo.activo, tipo.id_tipo_uniforme),
    )
    conn.commit()


def soft_delete(id_tipo: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE tipo_uniforme SET activo = 0 WHERE id_tipo_uniforme = ?", (id_tipo,))
    conn.commit()
