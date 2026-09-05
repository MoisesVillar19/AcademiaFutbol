from services import auth_service
from utils.validators import validate_not_empty


def iniciar_sesion(username: str, password: str) -> tuple[bool, str, dict | None]:
    error = validate_not_empty(username, "Usuario")
    if error:
        return False, error, None

    error = validate_not_empty(password, "Contraseña")
    if error:
        return False, error, None

    usuario = auth_service.login(username, password)
    if not usuario:
        return False, "Credenciales incorrectas o usuario desactivado", None

    return True, "Inicio de sesión exitoso", usuario


def cerrar_sesion() -> None:
    auth_service.logout()


def necesita_cambiar_password() -> bool:
    return auth_service.requiere_cambio_password()


def cambiar_password(password_actual: str, password_nuevo: str,
                     confirmar_password: str) -> tuple[bool, str]:
    if not password_actual or not password_nuevo or not confirmar_password:
        return False, "Todos los campos son obligatorios"

    if password_nuevo != confirmar_password:
        return False, "Las contraseñas nuevas no coinciden"

    return auth_service.cambiar_password(password_actual, password_nuevo)


def restablecer_password_emergencia(pin: str, username: str,
                                    nueva_password: str) -> tuple[bool, str]:
    if not pin:
        return False, "Ingrese el PIN de emergencia"
    if not nueva_password:
        return False, "La nueva contraseña es obligatoria"

    from utils.constants import DEFAULT_ADMIN_USER
    usuario_destino = username or DEFAULT_ADMIN_USER
    return auth_service.restablecer_password_con_pin(pin, usuario_destino, nueva_password)


def obtener_usuario_actual() -> dict | None:
    return auth_service.obtener_usuario_actual()


def esta_logueado() -> bool:
    return auth_service.esta_logueado()


def es_admin() -> bool:
    return auth_service.es_admin()
