from services import usuario_service, auth_service
from utils.validators import validate_not_empty, validate_rol, validate_documento


def _requerir_admin() -> tuple[bool, str]:
    if not auth_service.es_admin():
        return False, "Acceso denegado: solo un administrador puede gestionar usuarios"
    return True, ""


def crear_usuario(persona_data: dict, username: str, rol: str) -> tuple[bool, str, int | None]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg, None

    error = validate_not_empty(username, "Usuario")
    if error:
        return False, error, None

    error = validate_not_empty(rol, "Rol")
    if error:
        return False, error, None

    if not validate_rol(rol):
        return False, "Rol no válido. Use ADMIN o SECRETARIA", None

    dni = persona_data.get("dni", "")
    tipo_doc = persona_data.get("tipo_documento", "DNI")
    if dni and not validate_documento(dni, tipo_doc):
        if tipo_doc == "CARNET":
            return False, "El Carnet debe tener 9 dígitos", None
        return False, "El DNI debe tener 8 dígitos", None

    return usuario_service.crear_usuario(persona_data, username, rol)


def editar_usuario(id_usuario: int, data: dict) -> tuple[bool, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg

    if "username" in data:
        error = validate_not_empty(data["username"], "Usuario")
        if error:
            return False, error

    if "rol" in data:
        if not validate_rol(data["rol"]):
            return False, "Rol no válido. Use ADMIN o SECRETARIA"

    if "dni" in data and data["dni"]:
        tipo_doc = data.get("tipo_documento", "DNI")
        if not validate_documento(data["dni"], tipo_doc):
            if tipo_doc == "CARNET":
                return False, "El Carnet debe tener 9 dígitos"
            return False, "El DNI debe tener 8 dígitos"

    return usuario_service.editar_usuario(id_usuario, data)


def activar_usuario(id_usuario: int) -> tuple[bool, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg
    return usuario_service.activar_usuario(id_usuario)


def desactivar_usuario(id_usuario: int) -> tuple[bool, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg
    return usuario_service.desactivar_usuario(id_usuario)


def restablecer_password(id_usuario: int) -> tuple[bool, str, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg, None
    return usuario_service.restablecer_password(id_usuario)


def listar_usuarios(activo: int | None = None) -> list[dict]:
    return usuario_service.listar_usuarios(activo=activo)


def listar_permisos_rol(rol: str) -> set:
    permitido, msg = _requerir_admin()
    if not permitido:
        return set()
    from repositories import rol_permiso_repository
    perms = rol_permiso_repository.obtener_por_rol(rol)
    if not perms:
        from utils.constants import PERMISOS_ROL
        perms = set(PERMISOS_ROL.get(rol, set()))
    return perms


def guardar_permisos_rol(rol: str, modulos) -> tuple[bool, str]:
    permitido, msg = _requerir_admin()
    if not permitido:
        return False, msg
    if rol == "ADMIN":
        return False, "El rol ADMIN siempre tiene acceso total (fijo)"
    if not validate_rol(rol):
        return False, "Rol no válido. Use ADMIN o SECRETARIA"
    mods = [m for m in (modulos or []) if m]
    if not mods:
        return False, "El rol debe conservar al menos 1 módulo"
    try:
        from repositories import rol_permiso_repository
        rol_permiso_repository.reemplazar(rol, mods)
    except ValueError as e:
        return False, str(e)
    auth_service.limpiar_cache_permisos()
    return True, f"Permisos de {rol} actualizados ({len(mods)} módulos)"


def obtener_usuario(id_usuario: int) -> dict | None:
    return usuario_service.obtener_usuario(id_usuario)
