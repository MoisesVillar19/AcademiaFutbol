from database.connection import get_connection, fetch_one, fetch_all


def insertar(nombre: str, edad_min: int, edad_max: int) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO categoria (nombre, edad_min, edad_max) VALUES (?, ?, ?)",
        (nombre, edad_min, edad_max),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_categoria: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM categoria WHERE id_categoria = ?",
        (id_categoria,),
    )


def obtener_activas() -> list[dict]:
    return fetch_all(
        "SELECT * FROM categoria WHERE activo = 1 ORDER BY edad_min",
    )


def obtener_por_edad(edad: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM categoria WHERE ? BETWEEN edad_min AND edad_max AND activo = 1",
        (edad,),
    )


def obtener_todas() -> list[dict]:
    return fetch_all("SELECT * FROM categoria ORDER BY edad_min")


def existe_nombre(nombre: str, exclude_id: int = 0) -> bool:
    if exclude_id:
        row = fetch_one(
            "SELECT id_categoria FROM categoria WHERE nombre = ? AND id_categoria != ?",
            (nombre, exclude_id),
        )
    else:
        row = fetch_one(
            "SELECT id_categoria FROM categoria WHERE nombre = ?",
            (nombre,),
        )
    return row is not None


def actualizar(id_categoria: int, nombre: str, edad_min: int, edad_max: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE categoria SET nombre = ?, edad_min = ?, edad_max = ? WHERE id_categoria = ?",
        (nombre, edad_min, edad_max, id_categoria),
    )
    conn.commit()


def soft_delete(id_categoria: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE categoria SET activo = 0 WHERE id_categoria = ?",
        (id_categoria,),
    )
    conn.commit()
