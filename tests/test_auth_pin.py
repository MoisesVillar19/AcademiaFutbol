"""Tests de autenticacion y restablecimiento por PIN de emergencia."""
from services import auth_service
from repositories import usuario_repository
from controllers import login_controller
from utils.constants import DEFAULT_ADMIN_USER, PIN_EMERGENCIA_DEFECTO


def test_login_credenciales_correctas():
    usuario = auth_service.login(DEFAULT_ADMIN_USER, "admin123")
    assert usuario is not None
    assert usuario["rol"] == "ADMIN"
    # El hash NUNCA debe viajar en la sesion
    assert "password_hash" not in usuario


def test_login_password_incorrecta():
    assert auth_service.login(DEFAULT_ADMIN_USER, "wrong") is None


def test_login_usuario_inexistente():
    assert auth_service.login("fantasma", "x123456789") is None


def test_requiere_cambio_password_con_default():
    auth_service.login(DEFAULT_ADMIN_USER, "admin123")
    assert auth_service.requiere_cambio_password() is True


def test_pin_incorrecto_rechazado():
    exito, msg = login_controller.restablecer_password_emergencia(
        "pin_falso_123", "", "NuevaClave99")
    assert exito is False
    assert "PIN" in msg


def test_pin_vacio_rechazado():
    exito, msg = login_controller.restablecer_password_emergencia("", "", "NuevaClave99")
    assert exito is False


def test_password_corta_rechazada_aun_con_pin_valido():
    exito, msg = login_controller.restablecer_password_emergencia(
        PIN_EMERGENCIA_DEFECTO, "", "abc")
    assert exito is False


def test_pin_valido_restaura_password_admin():
    exito, msg = login_controller.restablecer_password_emergencia(
        PIN_EMERGENCIA_DEFECTO, "", "NuevaClave99")
    assert exito is True, msg

    usuario = usuario_repository.obtener_por_username(DEFAULT_ADMIN_USER)
    from utils.security import verify_password
    assert verify_password("NuevaClave99", usuario["password_hash"])

    # Login con la nueva clave funciona; con la vieja no
    assert auth_service.login(DEFAULT_ADMIN_USER, "NuevaClave99") is not None
    assert auth_service.login(DEFAULT_ADMIN_USER, "admin123") is None

    # Ya no requiere cambio de password (no coincide con el default)
    assert auth_service.requiere_cambio_password() is False


def test_pin_usuario_desactivado_rechazado(usuario_admin):
    from services import usuario_service
    exito, temp, id_u = usuario_service.crear_usuario(
        {"dni": "77788999", "nombres": "Temp", "apellidos": "User"},
        "temp_user", "SECRETARIA",
    )
    usuario_service.desactivar_usuario(id_u)

    exito, msg = login_controller.restablecer_password_emergencia(
        PIN_EMERGENCIA_DEFECTO, "temp_user", "AlgunaClave1")
    assert exito is False
    assert "desactivado" in msg.lower()


def test_cambiar_password_flujo_completo():
    auth_service.login(DEFAULT_ADMIN_USER, "admin123")

    exito, msg = auth_service.cambiar_password("incorrecta", "OtraClave77")
    assert exito is False

    exito, msg = auth_service.cambiar_password("admin123", "admin123")
    assert exito is False  # igual a la actual

    exito, msg = auth_service.cambiar_password("admin123", "MiClave2026")
    assert exito is True, msg

    assert auth_service.login(DEFAULT_ADMIN_USER, "MiClave2026") is not None
