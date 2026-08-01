from repositories import usuario_repository, persona_repository
from services import auditoria_service
from utils.security import verify_password, hash_password
from utils.logger import logger


_usuario_actual: dict | None = None


def login(username: str, password: str) -> dict | None:
    global _usuario_actual

    usuario = usuario_repository.obtener_por_username(username)
    if not usuario:
        logger.warning(f"Intento de login fallido: usuario '{username}' no encontrado")
        return None

    if usuario["activo"] == 0:
        logger.warning(f"Intento de login fallido: usuario '{username}' desactivado")
        return None

    if not verify_password(password, usuario["password_hash"]):
        logger.warning(f"Intento de login fallido: contraseña incorrecta para '{username}'")
        return None

    persona = persona_repository.obtener_por_id(usuario["id_persona"])

    _usuario_actual = {
        "id_usuario": usuario["id_usuario"],
        "username": usuario["username"],
        "rol": usuario["rol"],
        "id_persona": usuario["id_persona"],
        "nombres": persona["nombres"] if persona else "",
        "apellidos": persona["apellidos"] if persona else "",
        "dni": persona["dni"] if persona else "",
        "password_hash": usuario["password_hash"],
    }

    auditoria_service.registrar_log(
        id_usuario=usuario["id_usuario"],
        tabla_afectada="usuario",
        id_registro=usuario["id_usuario"],
        accion="LOGIN",
    )

    logger.info(f"Login exitoso: '{username}' (rol: {usuario['rol']})")
    return _usuario_actual


def logout() -> None:
    global _usuario_actual
    if _usuario_actual:
        logger.info(f"Logout: '{_usuario_actual['username']}'")
    _usuario_actual = None


def obtener_usuario_actual() -> dict | None:
    return _usuario_actual


def esta_logueado() -> bool:
    return _usuario_actual is not None


def es_admin() -> bool:
    return _usuario_actual is not None and _usuario_actual["rol"] == "ADMIN"


def requiere_cambio_password() -> bool:
    if not _usuario_actual:
        return False
    from utils.constants import DEFAULT_ADMIN_PASS
    return verify_password(DEFAULT_ADMIN_PASS, _usuario_actual["password_hash"])


def cambiar_password(password_actual: str, password_nuevo: str) -> tuple[bool, str]:
    if not _usuario_actual:
        return False, "No hay sesión activa"

    if not verify_password(password_actual, _usuario_actual["password_hash"]):
        return False, "La contraseña actual es incorrecta"

    if len(password_nuevo) < 6:
        return False, "La nueva contraseña debe tener al menos 6 caracteres"

    if password_actual == password_nuevo:
        return False, "La nueva contraseña debe ser diferente a la actual"

    nuevo_hash = hash_password(password_nuevo)
    usuario_repository.cambiar_password(_usuario_actual["id_usuario"], nuevo_hash)

    _usuario_actual["password_hash"] = nuevo_hash

    auditoria_service.registrar_log(
        id_usuario=_usuario_actual["id_usuario"],
        tabla_afectada="usuario",
        id_registro=_usuario_actual["id_usuario"],
        accion="CAMBIO_PASSWORD",
    )

    logger.info(f"Contraseña cambiada: '{_usuario_actual['username']}'")
    return True, "Contraseña cambiada correctamente"
