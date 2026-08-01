from repositories import log_repository
from utils.logger import logger


def registrar_log(id_usuario: int, tabla_afectada: str, id_registro: int,
                  accion: str, valor_anterior: str = "", valor_nuevo: str = "") -> int:
    try:
        log_id = log_repository.insertar(
            id_usuario=id_usuario,
            tabla_afectada=tabla_afectada,
            id_registro=id_registro,
            accion=accion,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
        )
        return log_id
    except Exception as e:
        logger.error(f"Error al registrar log: {e}")
        raise


def registrar_insert(id_usuario: int, tabla: str, id_registro: int, valores_nuevos: str = "") -> int:
    return registrar_log(id_usuario, tabla, id_registro, "INSERT", "", valores_nuevos)


def registrar_update(id_usuario: int, tabla: str, id_registro: int,
                     valores_anteriores: str, valores_nuevos: str) -> int:
    return registrar_log(id_usuario, tabla, id_registro, "UPDATE", valores_anteriores, valores_nuevos)


def registrar_desactivacion(id_usuario: int, tabla: str, id_registro: int,
                            valores_anteriores: str, valores_nuevos: str) -> int:
    return registrar_log(id_usuario, tabla, id_registro, "DESACTIVACION", valores_anteriores, valores_nuevos)


def obtener_logs(limit: int = 100, offset: int = 0) -> list[dict]:
    return log_repository.obtener_todos(limit=limit, offset=offset)


def obtener_logs_por_tabla(tabla: str, limit: int = 100) -> list[dict]:
    return log_repository.obtener_por_tabla(tabla, limit=limit)


def obtener_logs_por_usuario(id_usuario: int, limit: int = 100) -> list[dict]:
    return log_repository.obtener_por_usuario(id_usuario, limit=limit)


def obtener_logs_por_fecha(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    return log_repository.obtener_por_fecha(fecha_inicio, fecha_fin)
