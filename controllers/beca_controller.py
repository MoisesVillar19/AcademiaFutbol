from services import beca_service, auth_service


def _requerir_admin() -> tuple[bool, str]:
    if not auth_service.es_admin():
        return False, "Acceso denegado: solo un administrador gestiona becas"
    return True, ""


def crear_beca(data: dict) -> tuple[bool, str, int | None]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg, None
    return beca_service.crear_beca(data)


def editar_beca(id_beca: int, data: dict) -> tuple[bool, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg
    return beca_service.editar_beca(id_beca, data)


def desactivar_beca(id_beca: int) -> tuple[bool, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg
    return beca_service.desactivar_beca(id_beca)


def activar_beca(id_beca: int) -> tuple[bool, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg
    return beca_service.activar_beca(id_beca)


def listar_becas() -> list[dict]:
    return beca_service.listar_becas(activo=1)


def listar_todas() -> list[dict]:
    return beca_service.listar_becas(activo=None)
