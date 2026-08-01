from database.connection import get_connection, fetch_one, fetch_all
from models.beca import Beca


def insertar(beca: Beca) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO beca
           (nombre, tipo, valor, observacion, activo)
           VALUES (?, ?, ?, ?, ?)""",
        (beca.nombre, beca.tipo, beca.valor, beca.observacion, beca.activo),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_beca: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM beca WHERE id_beca = ?",
        (id_beca,),
    )


def obtener_todas(activo: int | None = None) -> list[dict]:
    if activo is not None:
        return fetch_all(
            "SELECT * FROM beca WHERE activo = ?",
            (activo,),
        )
    return fetch_all("SELECT * FROM beca")


def actualizar(beca: Beca) -> None:
    conn = get_connection()
    conn.execute(
        """UPDATE beca SET
           nombre = ?, tipo = ?, valor = ?, observacion = ?, activo = ?
           WHERE id_beca = ?""",
        (beca.nombre, beca.tipo, beca.valor, beca.observacion, beca.activo, beca.id_beca),
    )
    conn.commit()


def soft_delete(id_beca: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE beca SET activo = 0 WHERE id_beca = ?",
        (id_beca,),
    )
    conn.commit()
