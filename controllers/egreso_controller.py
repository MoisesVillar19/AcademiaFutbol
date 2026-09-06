from services import egreso_service, auth_service


def registrar_egreso(data: dict) -> tuple[bool, str, int | None]:
    if not auth_service.es_admin():
        return False, "Solo ADMIN puede registrar egresos", None
    if not data.get("id_usuario"):
        data["id_usuario"] = auth_service.id_usuario_sesion_or_system()
    return egreso_service.registrar_egreso(data)


def listar_egresos(fecha_inicio: str | None = None, fecha_fin: str | None = None) -> list[dict]:
    if not auth_service.es_admin():
        return []
    return egreso_service.listar_egresos(fecha_inicio, fecha_fin)


def reporte_ingresos_vs_egresos(fecha_inicio: str, fecha_fin: str) -> dict:
    if not auth_service.es_admin():
        return {}
    return egreso_service.reporte_ingresos_vs_egresos(fecha_inicio, fecha_fin)
