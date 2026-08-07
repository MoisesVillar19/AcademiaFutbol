from database.connection import get_connection, fetch_one, fetch_all
from models.persona import Persona
from utils.dates import get_now


def insertar(persona: Persona) -> int:
    conn = get_connection()
    now = get_now()
    cursor = conn.execute(
        """INSERT INTO persona
           (dni, tipo_documento, nombres, apellidos, fecha_nacimiento, sexo, direccion, telefono, correo, activo, fecha_creacion, fecha_actualizacion)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            persona.dni,
            persona.tipo_documento,
            persona.nombres,
            persona.apellidos,
            persona.fecha_nacimiento,
            persona.sexo,
            persona.direccion,
            persona.telefono,
            persona.correo,
            persona.activo,
            now,
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_persona: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM persona WHERE id_persona = ?",
        (id_persona,),
    )


def obtener_por_dni(dni: str) -> dict | None:
    return fetch_one(
        "SELECT * FROM persona WHERE dni = ?",
        (dni,),
    )


def existe_dni(dni: str, exclude_id: int | None = None) -> bool:
    if exclude_id:
        row = fetch_one(
            "SELECT id_persona FROM persona WHERE dni = ? AND id_persona != ?",
            (dni, exclude_id),
        )
    else:
        row = fetch_one(
            "SELECT id_persona FROM persona WHERE dni = ?",
            (dni,),
        )
    return row is not None


def actualizar(persona: Persona) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        """UPDATE persona SET
           dni = ?, tipo_documento = ?, nombres = ?, apellidos = ?, fecha_nacimiento = ?,
           sexo = ?, direccion = ?, telefono = ?, correo = ?,
           activo = ?, fecha_actualizacion = ?
           WHERE id_persona = ?""",
        (
            persona.dni,
            persona.tipo_documento,
            persona.nombres,
            persona.apellidos,
            persona.fecha_nacimiento,
            persona.sexo,
            persona.direccion,
            persona.telefono,
            persona.correo,
            persona.activo,
            now,
            persona.id_persona,
        ),
    )
    conn.commit()


def obtener_todos(activo: int | None = None) -> list[dict]:
    if activo is not None:
        return fetch_all(
            "SELECT * FROM persona WHERE activo = ?",
            (activo,),
        )
    return fetch_all("SELECT * FROM persona")
