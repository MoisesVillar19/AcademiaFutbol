"""Tests de control de acceso por rol (ADMIN vs SECRETARIA) en controllers."""
from controllers import usuario_controller, configuracion_controller, auditoria_controller


def test_secretaria_no_crea_usuarios(usuario_secretaria):
    exito, msg, _ = usuario_controller.crear_usuario(
        {"dni": "12345678", "nombres": "X", "apellidos": "Y"},
        "nuevo_user", "SECRETARIA",
    )
    assert exito is False
    assert "admin" in msg.lower()


def test_secretaria_no_edita_usuarios(usuario_secretaria):
    exito, msg = usuario_controller.editar_usuario(1, {"nombres": "Hack"})
    assert exito is False


def test_secretaria_no_desactiva_usuarios(usuario_secretaria):
    exito, msg = usuario_controller.desactivar_usuario(2)
    assert exito is False


def test_secretaria_no_restaura_password(usuario_secretaria):
    exito, msg, temp = usuario_controller.restablecer_password(2)
    assert exito is False


def test_admin_puede_crear_y_desactivar_usuarios(usuario_admin):
    exito, msg, id_usuario = usuario_controller.crear_usuario(
        {"dni": "98765432", "nombres": "Nuevo", "apellidos": "Usuario"},
        "user_ctrl_test", "SECRETARIA",
    )
    assert exito is True, msg
    assert id_usuario > 0

    exito, msg = usuario_controller.desactivar_usuario(id_usuario)
    assert exito is True, msg


def test_secretaria_no_actualiza_configuracion(usuario_secretaria):
    exito, msg = configuracion_controller.actualizar_configuracion({"nombre_academia": "Hack"})
    assert exito is False


def test_admin_actualiza_configuracion(usuario_admin):
    exito, msg = configuracion_controller.actualizar_configuracion(
        {"nombre_academia": "Academia Test QA"}
    )
    assert exito is True

    config = configuracion_controller.obtener_configuracion()
    assert config["nombre_academia"] == "Academia Test QA"


def test_auditoria_bloqueada_para_secretaria(usuario_secretaria, crear_persona):
    # Generar actividad para que existan logs (el fixture secretaria ya hizo LOGIN)
    logs = auditoria_controller.consultar_logs()
    assert logs == []
    assert auditoria_controller.filtrar_por_tabla("usuario") == []
    assert auditoria_controller.filtrar_por_usuario(1) == []


def test_auditoria_visible_para_admin(usuario_admin, crear_persona):
    logs = auditoria_controller.consultar_logs(limit=50)
    assert isinstance(logs, list)
    assert len(logs) >= 1  # al menos el LOGIN del admin


def test_sin_sesion_no_accede_a_gestion_usuarios():
    from services import auth_service
    auth_service.logout()
    exito, msg, _ = usuario_controller.crear_usuario({}, "x", "ADMIN")
    assert exito is False
