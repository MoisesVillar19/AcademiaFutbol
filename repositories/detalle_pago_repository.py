from database.connection import get_connection, fetch_one, fetch_all


def insertar(id_pago: int, id_cuota: int, monto_pagado: float) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO detalle_pago
           (id_pago, id_cuota, monto_pagado)
           VALUES (?, ?, ?)""",
        (id_pago, id_cuota, monto_pagado),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_pago(id_pago: int) -> list[dict]:
    return fetch_all(
        """SELECT dp.*, c.periodo, c.monto_total as cuota_total,
                  c.fecha_vencimiento, c.estado as cuota_estado
           FROM detalle_pago dp
           JOIN cuota c ON dp.id_cuota = c.id_cuota
           WHERE dp.id_pago = ?""",
        (id_pago,),
    )


def obtener_por_cuota(id_cuota: int) -> list[dict]:
    return fetch_all(
        """SELECT dp.*, p.numero_recibo, p.fecha_pago, p.metodo_pago
           FROM detalle_pago dp
           JOIN pago p ON dp.id_pago = p.id_pago
           WHERE dp.id_cuota = ? AND p.activo = 1
           ORDER BY p.fecha_pago""",
        (id_cuota,),
    )


def sumar_pagos_por_cuota(id_cuota: int) -> float:
    row = fetch_one(
        """SELECT COALESCE(SUM(dp.monto_pagado), 0) as total
           FROM detalle_pago dp
           JOIN pago p ON dp.id_pago = p.id_pago
           WHERE dp.id_cuota = ? AND p.activo = 1""",
        (id_cuota,),
    )
    return row["total"] if row else 0.0
