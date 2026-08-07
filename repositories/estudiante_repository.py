from database.connection import get_connection, fetch_one, fetch_all
from models.estudiante import Estudiante
from utils.dates import get_now


def insertar(estudiante: Estudiante) -> int:
    conn = get_connection()
    now = get_now()
    cursor = conn.execute(
        """INSERT INTO estudiante
           (id_persona, estado, fecha_ingreso, fecha_retiro, activo)
           VALUES (?, ?, ?, ?, ?)""",
        (
            estudiante.id_persona,
            estudiante.estado,
            estudiante.fecha_ingreso,
            estudiante.fecha_retiro,
            estudiante.activo,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_estudiante: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM estudiante WHERE id_estudiante = ?",
        (id_estudiante,),
    )


def obtener_por_persona(id_persona: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM estudiante WHERE id_persona = ?",
        (id_persona,),
    )


def obtener_todos(activo: int | None = None, estado=None) -> list[dict]:
    sql = """
        SELECT e.*, p.dni, p.nombres, p.apellidos, p.fecha_nacimiento,
               p.sexo, p.telefono, p.correo
        FROM estudiante e
        JOIN persona p ON e.id_persona = p.id_persona
    """
    conditions = []
    params = []
    if activo is not None:
        conditions.append("e.activo = ?")
        params.append(activo)
    if estado is not None:
        if isinstance(estado, (list, tuple)):
            placeholders = ",".join("?" * len(estado))
            conditions.append(f"e.estado IN ({placeholders})")
            params.extend(estado)
        else:
            conditions.append("e.estado = ?")
            params.append(estado)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    return fetch_all(sql, tuple(params))


def obtener_por_id_con_persona(id_estudiante: int) -> dict | None:
    return fetch_one(
        """SELECT e.*, p.dni, p.nombres, p.apellidos, p.fecha_nacimiento,
                  p.sexo, p.direccion, p.telefono, p.correo
           FROM estudiante e
           JOIN persona p ON e.id_persona = p.id_persona
           WHERE e.id_estudiante = ?""",
        (id_estudiante,),
    )


def actualizar(estudiante: Estudiante) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        """UPDATE estudiante SET
           id_persona = ?, estado = ?, fecha_ingreso = ?,
           fecha_retiro = ?, activo = ?
           WHERE id_estudiante = ?""",
        (
            estudiante.id_persona,
            estudiante.estado,
            estudiante.fecha_ingreso,
            estudiante.fecha_retiro,
            estudiante.activo,
            estudiante.id_estudiante,
        ),
    )
    conn.commit()


def cambiar_estado(id_estudiante: int, estado: str, fecha_retiro: str | None = None) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE estudiante SET estado = ?, fecha_retiro = ? WHERE id_estudiante = ?",
        (estado, fecha_retiro, id_estudiante),
    )
    conn.commit()


def soft_delete(id_estudiante: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE estudiante SET activo = 0 WHERE id_estudiante = ?",
        (id_estudiante,),
    )
    conn.commit()
