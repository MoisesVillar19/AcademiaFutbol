from repositories import egreso_repository
from models.egreso import Egreso
from services import auditoria_service
from utils.logger import logger
from utils.validators import validate_not_empty

CONCEPTOS_VALIDOS = ("PROFESOR", "PERSONAL", "CAMPEONATO_FIJO", "ARBITRAJE", "VIATICOS")


def registrar_egreso(data: dict) -> tuple[bool, str, int | None]:
    concepto = data.get("concepto", "").strip().upper()
    monto = data.get("monto")
    fecha = data.get("fecha")
    if concepto not in CONCEPTOS_VALIDOS:
        return False, f"Concepto no válido. Permitidos: {', '.join(CONCEPTOS_VALIDOS)}", None
    try:
        monto_f = float(monto)
        if monto_f <= 0:
            return False, "Monto debe ser mayor a 0", None
    except (ValueError, TypeError) as e:
        logger.warning(f"Egreso monto inválido: {monto} ({e})")
        return False, "Monto inválido", None
    err = validate_not_empty(fecha, "Fecha")
    if err:
        return False, err, None
    id_usuario = data.get("id_usuario") or auditoria_service.id_usuario_sesion()
    egreso = Egreso(
        concepto=concepto,
        monto=round(monto_f, 2),
        fecha=fecha,
        responsable=data.get("responsable", ""),
        id_usuario=id_usuario,
        observacion=data.get("observacion", ""),
    )
    id_egreso = egreso_repository.insertar(egreso)
    auditoria_service.registrar_insert(id_usuario, "egreso", id_egreso, f"concepto={concepto}, monto={monto_f}")
    logger.info(f"Egreso registrado: {concepto} {monto_f}")
    return True, "Egreso registrado correctamente", id_egreso


def listar_egresos(fecha_inicio: str | None = None, fecha_fin: str | None = None) -> list[dict]:
    return egreso_repository.obtener_todos(fecha_inicio, fecha_fin)


def reporte_ingresos_vs_egresos(fecha_inicio: str, fecha_fin: str) -> dict:
    from repositories import venta_repository, pago_repository
    ingresos_ventas = venta_repository.sumar_por_periodo(fecha_inicio, fecha_fin)
    ingresos_pagos = pago_repository.sumar_por_fecha(fecha_inicio, fecha_fin) if hasattr(pago_repository, "sumar_por_fecha") else 0
    egresos = egreso_repository.sumar_por_periodo(fecha_inicio, fecha_fin)
    total_ingresos = round(ingresos_ventas + ingresos_pagos, 2)
    neto = round(total_ingresos - egresos, 2)
    return {"ingresos_ventas": ingresos_ventas, "ingresos_pagos": ingresos_pagos, "total_ingresos": total_ingresos, "egresos": egresos, "neto": neto}
