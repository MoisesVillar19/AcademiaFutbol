from database.connection import get_connection, fetch_one
from utils.constants import (
    CATEGORIA_INICIAL,
    CATEGORIA_PRODUCTO_INICIAL,
    DEFAULT_ADMIN_USER,
    DEFAULT_ADMIN_PASS,
    PIN_EMERGENCIA_DEFECTO,
)
from utils.security import hash_password
from utils.dates import get_now


def seed_database() -> None:
    conn = get_connection()
    now = get_now()

    admin_user = fetch_one(
        "SELECT id_usuario FROM usuario WHERE username = ?",
        (DEFAULT_ADMIN_USER,),
    )
    if not admin_user:
        conn.execute(
            """INSERT INTO persona (dni, nombres, apellidos, fecha_creacion)
               VALUES (?, ?, ?, ?)""",
            ("00000000", "Admin", "Sistema", now),
        )
        persona_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            """INSERT INTO usuario (id_persona, username, password_hash, rol, fecha_creacion)
               VALUES (?, ?, ?, ?, ?)""",
            (persona_id, DEFAULT_ADMIN_USER, hash_password(DEFAULT_ADMIN_PASS), "ADMIN", now),
        )

    for nombre, edad_min, edad_max in CATEGORIA_INICIAL:
        exists = fetch_one(
            "SELECT id_categoria FROM categoria WHERE nombre = ?",
            (nombre,),
        )
        if not exists:
            conn.execute(
                "INSERT INTO categoria (nombre, edad_min, edad_max) VALUES (?, ?, ?)",
                (nombre, edad_min, edad_max),
            )

    for nombre in CATEGORIA_PRODUCTO_INICIAL:
        exists = fetch_one(
            "SELECT id_categoria_producto FROM categoria_producto WHERE nombre = ?",
            (nombre,),
        )
        if not exists:
            conn.execute(
                "INSERT INTO categoria_producto (nombre) VALUES (?)",
                (nombre,),
            )

    config = fetch_one("SELECT id_configuracion, pin_emergencia FROM configuracion WHERE id_configuracion = 1")
    if not config:
        conn.execute(
            """INSERT INTO configuracion
               (id_configuracion, nombre_academia, dias_por_vencer, permitir_multiples_becas,
                backup_automatico, frecuencia_backup, ruta_backup, pin_emergencia, fecha_actualizacion)
               VALUES (1, 'Academia Deportiva', 3, 1, 1, 7, 'backups/', ?, ?)""",
            (hash_password(PIN_EMERGENCIA_DEFECTO), now),
        )
    elif not config.get("pin_emergencia"):
        conn.execute(
            "UPDATE configuracion SET pin_emergencia = ? WHERE id_configuracion = 1",
            (hash_password(PIN_EMERGENCIA_DEFECTO),),
        )

    conn.commit()


if __name__ == "__main__":
    seed_database()
    print("Datos iniciales insertados correctamente.")
