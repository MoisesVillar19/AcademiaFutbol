from services import venta_service, auth_service


def registrar_venta(data: dict) -> tuple[bool, str, int | None]:
    if not auth_service.esta_logueado():
        return False, "Sesión requerida", None
    if not data.get("id_usuario"):
        data["id_usuario"] = auth_service.id_usuario_sesion_or_system()
    return venta_service.registrar_venta(data)


def listar_ventas(fecha_inicio: str | None = None, fecha_fin: str | None = None, tipo_venta: str | None = None) -> list[dict]:
    return venta_service.listar_ventas(fecha_inicio, fecha_fin, tipo_venta)


def obtener_venta(id_venta: int) -> dict | None:
    return venta_service.obtener_venta(id_venta)
