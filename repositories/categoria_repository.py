from database.connection import get_connection, fetch_one, fetch_all


TIPOS_VALIDOS = ("ACADEMIA", "CAMPEONATO", "SERVICIO")


def insertar(nombre: str, edad_min: int | None = None, edad_max: int | None = None, tipo: str = "ACADEMIA") -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO categoria (nombre, edad_min, edad_max, tipo) VALUES (?, ?, ?, ?)",
        (nombre, edad_min, edad_max, tipo),
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
        "SELECT * FROM categoria WHERE activo = 1 ORDER BY tipo, COALESCE(edad_min, 9999)",
    )


def obtener_por_tipo(tipo: str) -> list[dict]:
    return fetch_all(
        "SELECT * FROM categoria WHERE tipo = ? AND activo = 1 ORDER BY COALESCE(edad_min, 9999)",
        (tipo,),
    )


def obtener_por_edad(edad: int) -> dict | None:
    return fetch_one(
        """SELECT * FROM categoria
           WHERE tipo = 'ACADEMIA' AND edad_min IS NOT NULL AND edad_max IS NOT NULL
             AND ? BETWEEN edad_min AND edad_max AND activo = 1""",
        (edad,),
    )


def obtener_todas() -> list[dict]:
    return fetch_all("SELECT * FROM categoria ORDER BY tipo, COALESCE(edad_min, 9999)")


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


def actualizar(id_categoria: int, nombre: str, edad_min: int | None, edad_max: int | None, tipo: str = "ACADEMIA") -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE categoria SET nombre = ?, edad_min = ?, edad_max = ?, tipo = ? WHERE id_categoria = ?",
        (nombre, edad_min, edad_max, tipo, id_categoria),
    )
    conn.commit()


def soft_delete(id_categoria: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE categoria SET activo = 0 WHERE id_categoria = ?",
        (id_categoria,),
    )
    conn.commit()
