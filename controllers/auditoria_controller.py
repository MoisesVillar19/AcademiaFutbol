from services import auditoria_service
from services import auth_service
from utils.logger import logger


def consultar_logs(limit: int = 100, offset: int = 0) -> list[dict]:
    if not auth_service.es_admin():
        logger.warning("Intento de acceso a auditoría sin permisos ADMIN")
        return []

    return auditoria_service.obtener_logs(limit=limit, offset=offset)


def filtrar_por_tabla(tabla: str, limit: int = 100) -> list[dict]:
    if not auth_service.es_admin():
        return []

    return auditoria_service.obtener_logs_por_tabla(tabla, limit=limit)


def filtrar_por_usuario(id_usuario: int, limit: int = 100) -> list[dict]:
    if not auth_service.es_admin():
        return []

    return auditoria_service.obtener_logs_por_usuario(id_usuario, limit=limit)


def filtrar_por_fecha(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    if not auth_service.es_admin():
        return []

    return auditoria_service.obtener_logs_por_fecha(fecha_inicio, fecha_fin)


def puede_acceder_auditoria() -> bool:
    return auth_service.es_admin()
