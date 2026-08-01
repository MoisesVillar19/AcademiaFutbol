from services import usuario_service
from utils.validators import validate_not_empty, validate_rol, validate_dni


def crear_usuario(persona_data: dict, username: str, rol: str) -> tuple[bool, str, int | None]:
    error = validate_not_empty(username, "Usuario")
    if error:
        return False, error, None

    error = validate_not_empty(rol, "Rol")
    if error:
        return False, error, None

    if not validate_rol(rol):
        return False, "Rol no válido. Use ADMIN o SECRETARIA", None

    dni = persona_data.get("dni", "")
    if dni and not validate_dni(dni):
        return False, "El DNI debe tener 8 dígitos", None

    return usuario_service.crear_usuario(persona_data, username, rol)


def editar_usuario(id_usuario: int, data: dict) -> tuple[bool, str]:
    if "username" in data:
        error = validate_not_empty(data["username"], "Usuario")
        if error:
            return False, error

    if "rol" in data:
        if not validate_rol(data["rol"]):
            return False, "Rol no válido. Use ADMIN o SECRETARIA"

    if "dni" in data and data["dni"]:
        if not validate_dni(data["dni"]):
            return False, "El DNI debe tener 8 dígitos"

    return usuario_service.editar_usuario(id_usuario, data)


def activar_usuario(id_usuario: int) -> tuple[bool, str]:
    return usuario_service.activar_usuario(id_usuario)


def desactivar_usuario(id_usuario: int) -> tuple[bool, str]:
    return usuario_service.desactivar_usuario(id_usuario)


def restablecer_password(id_usuario: int) -> tuple[bool, str, str]:
    return usuario_service.restablecer_password(id_usuario)


def listar_usuarios(activo: int | None = None) -> list[dict]:
    return usuario_service.listar_usuarios(activo=activo)


def obtener_usuario(id_usuario: int) -> dict | None:
    return usuario_service.obtener_usuario(id_usuario)
