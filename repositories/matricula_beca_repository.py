from database.connection import get_connection, fetch_one, fetch_all


def insertar(id_matricula: int, id_beca: int, observacion: str = "") -> int:
    conn = get_connection()
    from utils.dates import get_now
    now = get_now()
    cursor = conn.execute(
        """INSERT INTO matricula_beca
           (id_matricula, id_beca, fecha_asignacion, activo, observacion)
           VALUES (?, ?, ?, 1, ?)""",
        (id_matricula, id_beca, now, observacion),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_matricula(id_matricula: int) -> list[dict]:
    return fetch_all(
        """SELECT mb.*, b.nombre as beca_nombre, b.tipo as beca_tipo,
                  b.valor as beca_valor
           FROM matricula_beca mb
           JOIN beca b ON mb.id_beca = b.id_beca
           WHERE mb.id_matricula = ? AND mb.activo = 1""",
        (id_matricula,),
    )


def eliminar(id_matricula: int, id_beca: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE matricula_beca SET activo = 0 WHERE id_matricula = ? AND id_beca = ?",
        (id_matricula, id_beca),
    )
    conn.commit()
