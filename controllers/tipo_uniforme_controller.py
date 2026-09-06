from services import tipo_uniforme_service
from services import auth_service


def _es_admin() -> bool:
    return auth_service.es_admin()


def crear_tipo(data: dict) -> tuple[bool, str, int | None]:
    if not _es_admin():
        return False, "Solo ADMIN puede crear tipos de uniforme", None
    return tipo_uniforme_service.crear_tipo_uniforme(data)


def listar_tipos(activo: int | None = 1) -> list[dict]:
    return tipo_uniforme_service.listar_tipos(activo=activo)


def desactivar_tipo(id_tipo: int) -> tuple[bool, str]:
    if not _es_admin():
        return False, "Solo ADMIN puede desactivar"
    return tipo_uniforme_service.desactivar_tipo(id_tipo)
