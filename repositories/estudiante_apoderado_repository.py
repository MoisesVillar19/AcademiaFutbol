from database.connection import get_connection, fetch_one, fetch_all
from utils.dates import get_now


def insertar(id_estudiante: int, id_apoderado: int, es_principal: int = 0) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO estudiante_apoderado
           (id_estudiante, id_apoderado, es_principal, activo)
           VALUES (?, ?, ?, 1)""",
        (id_estudiante, id_apoderado, es_principal),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_estudiante(id_estudiante: int) -> list[dict]:
    return fetch_all(
        """SELECT ea.*, a.parentesco, a.ocupacion,
                  p.dni, p.nombres, p.apellidos, p.telefono
           FROM estudiante_apoderado ea
           JOIN apoderado a ON ea.id_apoderado = a.id_apoderado
           JOIN persona p ON a.id_persona = p.id_persona
           WHERE ea.id_estudiante = ? AND ea.activo = 1""",
        (id_estudiante,),
    )


def obtener_por_apoderado(id_apoderado: int) -> list[dict]:
    return fetch_all(
        """SELECT ea.*, e.estado,
                  p.dni, p.nombres, p.apellidos
           FROM estudiante_apoderado ea
           JOIN estudiante e ON ea.id_estudiante = e.id_estudiante
           JOIN persona p ON e.id_persona = p.id_persona
           WHERE ea.id_apoderado = ? AND ea.activo = 1""",
        (id_apoderado,),
    )


def tiene_principal(id_estudiante: int) -> bool:
    row = fetch_one(
        """SELECT id_estudiante_apoderado FROM estudiante_apoderado
           WHERE id_estudiante = ? AND es_principal = 1 AND activo = 1""",
        (id_estudiante,),
    )
    return row is not None


def marcar_principal(id_estudiante: int, id_apoderado: int) -> None:
    conn = get_connection()
    conn.execute(
        """UPDATE estudiante_apoderado SET es_principal = 0
           WHERE id_estudiante = ?""",
        (id_estudiante,),
    )
    conn.execute(
        """UPDATE estudiante_apoderado SET es_principal = 1
           WHERE id_estudiante = ? AND id_apoderado = ?""",
        (id_estudiante, id_apoderado),
    )
    conn.commit()


def existe_relacion(id_estudiante: int, id_apoderado: int) -> bool:
    row = fetch_one(
        """SELECT id_estudiante_apoderado FROM estudiante_apoderado
           WHERE id_estudiante = ? AND id_apoderado = ? AND activo = 1""",
        (id_estudiante, id_apoderado),
    )
    return row is not None


def eliminar(id_estudiante: int, id_apoderado: int) -> None:
    conn = get_connection()
    conn.execute(
        """UPDATE estudiante_apoderado SET activo = 0
           WHERE id_estudiante = ? AND id_apoderado = ?""",
        (id_estudiante, id_apoderado),
    )
    conn.commit()
