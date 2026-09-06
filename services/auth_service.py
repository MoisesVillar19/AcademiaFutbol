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
        logger.info(f"Logout: '{_usuario_actual.get('username','')}'")
    _usuario_actual = None


def obtener_usuario_actual() -> dict | None:
    return _usuario_actual


def id_usuario_sesion() -> int | None:
    """Retorna el id del usuario en sesion, o None si no hay sesion (fail-closed).
    Caller debe decidir fallback; auditoria usará 1 solo para seed."""
    return _usuario_actual["id_usuario"] if _usuario_actual else None


def id_usuario_sesion_or_system() -> int:
    """Compat: retorna 1 si no hay sesión (para seed/background). Loguea warning."""
    uid = id_usuario_sesion()
    if uid is None:
        logger.warning("Audit sin sesión → usando sistema (id=1)")
        return 1
    return uid


def esta_logueado() -> bool:
    return _usuario_actual is not None


def es_admin() -> bool:
    return _usuario_actual is not None and _usuario_actual["rol"] == "ADMIN"


def tiene_permiso(modulo: str) -> bool:
    """Matriz granular: ADMIN todo, otros según PERMISOS_ROL. modulo ej: 'pagos', 'ventas', 'inventario'."""
    if not _usuario_actual:
        return False
    if _usuario_actual["rol"] == "ADMIN":
        return True
    try:
        from utils.constants import PERMISOS_ROL
        perms = PERMISOS_ROL.get(_usuario_actual["rol"], set())
        return modulo.lower() in perms
    except Exception:
        return False


def es_rol(rol: str) -> bool:
    return _usuario_actual is not None and _usuario_actual["rol"] == rol


def requiere_cambio_password() -> bool:
    if not _usuario_actual:
        return False
    from utils.constants import DEFAULT_ADMIN_PASS
    usuario = usuario_repository.obtener_por_id(_usuario_actual["id_usuario"])
    if not usuario:
        return False
    return verify_password(DEFAULT_ADMIN_PASS, usuario["password_hash"])


def restablecer_password_con_pin(pin_emergencia: str, username: str,
                                 nueva_password: str) -> tuple[bool, str]:
    """Restablece la contrasena de un usuario validando el PIN de emergencia.

    El PIN se valida contra su hash almacenado en CONFIGURACION.pin_emergencia;
    nunca se compara texto plano en el codigo.
    """
    from services import configuracion_service

    if not pin_emergencia:
        return False, "Ingrese el PIN de emergencia"
    if len(nueva_password) < 6:
        return False, "La nueva contraseña debe tener al menos 6 caracteres"

    pin_hash = configuracion_service.obtener_valor("pin_emergencia")
    if not pin_hash or not verify_password(pin_emergencia, pin_hash):
        logger.warning(f"Intento de restablecimiento con PIN incorrecto (usuario: '{username}')")
        return False, "PIN de emergencia incorrecto"

    usuario = usuario_repository.obtener_por_username(username)
    if not usuario:
        return False, "Usuario no encontrado"
    if usuario["activo"] == 0:
        return False, "El usuario está desactivado"

    usuario_repository.cambiar_password(usuario["id_usuario"], hash_password(nueva_password))

    auditoria_service.registrar_log(
        id_usuario=usuario["id_usuario"],
        tabla_afectada="usuario",
        id_registro=usuario["id_usuario"],
        accion="RESTABLECER_PASSWORD_EMERGENCIA",
        valor_nuevo=f"username={username}",
    )

    logger.warning(f"Contraseña restablecida vía PIN de emergencia: '{username}'")
    return True, "Contraseña restablecida correctamente"


def cambiar_password(password_actual: str, password_nuevo: str) -> tuple[bool, str]:
    if not _usuario_actual:
        return False, "No hay sesión activa"

    usuario = usuario_repository.obtener_por_id(_usuario_actual["id_usuario"])
    if not usuario or not verify_password(password_actual, usuario["password_hash"]):
        return False, "La contraseña actual es incorrecta"

    if len(password_nuevo) < 6:
        return False, "La nueva contraseña debe tener al menos 6 caracteres"

    if password_actual == password_nuevo:
        return False, "La nueva contraseña debe ser diferente a la actual"

    nuevo_hash = hash_password(password_nuevo)
    usuario_repository.cambiar_password(_usuario_actual["id_usuario"], nuevo_hash)

    auditoria_service.registrar_log(
        id_usuario=_usuario_actual["id_usuario"],
        tabla_afectada="usuario",
        id_registro=_usuario_actual["id_usuario"],
        accion="CAMBIO_PASSWORD",
    )

    logger.info(f"Contraseña cambiada: '{_usuario_actual['username']}'")
    return True, "Contraseña cambiada correctamente"
