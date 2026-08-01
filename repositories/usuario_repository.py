from database.connection import get_connection, fetch_one, fetch_all
from models.usuario import Usuario
from utils.dates import get_now


def insertar(usuario: Usuario) -> int:
    conn = get_connection()
    now = get_now()
    cursor = conn.execute(
        """INSERT INTO usuario
           (id_persona, username, password_hash, rol, activo, fecha_creacion, fecha_actualizacion)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            usuario.id_persona,
            usuario.username,
            usuario.password_hash,
            usuario.rol,
            usuario.activo,
            now,
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_usuario: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM usuario WHERE id_usuario = ?",
        (id_usuario,),
    )


def obtener_por_username(username: str) -> dict | None:
    return fetch_one(
        "SELECT * FROM usuario WHERE username = ?",
        (username,),
    )


def obtener_todos(activo: int | None = None) -> list[dict]:
    if activo is not None:
        return fetch_all(
            "SELECT * FROM usuario WHERE activo = ?",
            (activo,),
        )
    return fetch_all("SELECT * FROM usuario")


def actualizar(usuario: Usuario) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        """UPDATE usuario SET
           id_persona = ?, username = ?, password_hash = ?, rol = ?,
           activo = ?, fecha_actualizacion = ?
           WHERE id_usuario = ?""",
        (
            usuario.id_persona,
            usuario.username,
            usuario.password_hash,
            usuario.rol,
            usuario.activo,
            now,
            usuario.id_usuario,
        ),
    )
    conn.commit()


def cambiar_password(id_usuario: int, password_hash: str) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        "UPDATE usuario SET password_hash = ?, fecha_actualizacion = ? WHERE id_usuario = ?",
        (password_hash, now, id_usuario),
    )
    conn.commit()


def soft_delete(id_usuario: int) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        "UPDATE usuario SET activo = 0, fecha_actualizacion = ? WHERE id_usuario = ?",
        (now, id_usuario),
    )
    conn.commit()


def existe_username(username: str, exclude_id: int | None = None) -> bool:
    if exclude_id:
        row = fetch_one(
            "SELECT id_usuario FROM usuario WHERE username = ? AND id_usuario != ?",
            (username, exclude_id),
        )
    else:
        row = fetch_one(
            "SELECT id_usuario FROM usuario WHERE username = ?",
            (username,),
        )
    return row is not None


def persona_tiene_usuario(id_persona: int) -> bool:
    row = fetch_one(
        "SELECT id_usuario FROM usuario WHERE id_persona = ?",
        (id_persona,),
    )
    return row is not None
