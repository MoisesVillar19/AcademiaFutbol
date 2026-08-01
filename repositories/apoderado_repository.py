from database.connection import get_connection, fetch_one, fetch_all
from models.apoderado import Apoderado
from utils.dates import get_now


def insertar(apoderado: Apoderado) -> int:
    conn = get_connection()
    now = get_now()
    cursor = conn.execute(
        """INSERT INTO apoderado
           (id_persona, parentesco, ocupacion, activo, fecha_creacion, fecha_actualizacion)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            apoderado.id_persona,
            apoderado.parentesco,
            apoderado.ocupacion,
            apoderado.activo,
            now,
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_apoderado: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM apoderado WHERE id_apoderado = ?",
        (id_apoderado,),
    )


def obtener_por_persona(id_persona: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM apoderado WHERE id_persona = ?",
        (id_persona,),
    )


def obtener_todos(activo: int | None = None) -> list[dict]:
    sql = """
        SELECT a.*, p.dni, p.nombres, p.apellidos, p.telefono, p.correo
        FROM apoderado a
        JOIN persona p ON a.id_persona = p.id_persona
    """
    if activo is not None:
        sql += " WHERE a.activo = ?"
        return fetch_all(sql, (activo,))
    return fetch_all(sql)


def obtener_por_id_con_persona(id_apoderado: int) -> dict | None:
    return fetch_one(
        """SELECT a.*, p.dni, p.nombres, p.apellidos, p.telefono, p.correo
           FROM apoderado a
           JOIN persona p ON a.id_persona = p.id_persona
           WHERE a.id_apoderado = ?""",
        (id_apoderado,),
    )


def actualizar(apoderado: Apoderado) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        """UPDATE apoderado SET
           id_persona = ?, parentesco = ?, ocupacion = ?,
           activo = ?, fecha_actualizacion = ?
           WHERE id_apoderado = ?""",
        (
            apoderado.id_persona,
            apoderado.parentesco,
            apoderado.ocupacion,
            apoderado.activo,
            now,
            apoderado.id_apoderado,
        ),
    )
    conn.commit()


def soft_delete(id_apoderado: int) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        "UPDATE apoderado SET activo = 0, fecha_actualizacion = ? WHERE id_apoderado = ?",
        (now, id_apoderado),
    )
    conn.commit()
