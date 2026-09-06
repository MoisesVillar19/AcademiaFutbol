from database.connection import get_connection, fetch_one, fetch_all
from models.egreso import Egreso


def insertar(egreso: Egreso) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO egreso (concepto, monto, fecha, responsable, id_usuario, observacion) VALUES (?, ?, ?, ?, ?, ?)",
        (egreso.concepto, egreso.monto, egreso.fecha, egreso.responsable, egreso.id_usuario, egreso.observacion),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_egreso: int) -> dict | None:
    return fetch_one("SELECT * FROM egreso WHERE id_egreso = ?", (id_egreso,))


def obtener_todos(fecha_inicio: str | None = None, fecha_fin: str | None = None) -> list[dict]:
    sql = "SELECT * FROM egreso WHERE 1=1"
    params: list = []
    if fecha_inicio:
        sql += " AND fecha >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        sql += " AND fecha <= ?"
        params.append(fecha_fin)
    sql += " ORDER BY fecha DESC"
    return fetch_all(sql, tuple(params))


def sumar_por_periodo(fecha_inicio: str, fecha_fin: str) -> float:
    row = fetch_one("SELECT COALESCE(SUM(monto),0) as total FROM egreso WHERE fecha BETWEEN ? AND ? AND activo = 1", (fecha_inicio, fecha_fin))
    return float(row["total"]) if row else 0.0


def soft_delete(id_egreso: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE egreso SET activo = 0 WHERE id_egreso = ?", (id_egreso,))
    conn.commit()


def eliminar(id_egreso: int) -> None:
    # Deprecado: usar soft_delete para RN-028
    soft_delete(id_egreso)
