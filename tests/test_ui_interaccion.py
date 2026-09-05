"""Tests de interaccion UI: las vistas delegan en controllers y muestran feedback."""
import pytest

pytestmark = pytest.mark.ui

from views.estudiantes.estudiante_view import EstudianteView
from views.pagos.pago_view import PagoView
from views.login.login_view import LoginView, RecuperarPasswordDialog
from controllers import estudiante_controller, pago_controller, login_controller


def _llenar_formulario_estudiante(vista, dni="12345678", nombres="Juan",
                                  apellidos="Perez"):
    vista.combo_tipo_doc.set("DNI")
    vista.entry_dni.delete(0, "end")
    vista.entry_dni.insert(0, dni)
    vista.entry_nombres.delete(0, "end")
    vista.entry_nombres.insert(0, nombres)
    vista.entry_apellidos.delete(0, "end")
    vista.entry_apellidos.insert(0, apellidos)
    vista.combo_sexo.set("M")


def _llenar_apoderado(vista, dni="87654321", nombres="Maria", apellidos="Perez"):
    """El formulario exige apoderado para crear un estudiante nuevo (RN-005)."""
    vista.combo_tipo_doc_ap.set("DNI")
    vista.entry_dni_ap.delete(0, "end")
    vista.entry_dni_ap.insert(0, dni)
    vista.entry_nombres_ap.delete(0, "end")
    vista.entry_nombres_ap.insert(0, nombres)
    vista.entry_apellidos_ap.delete(0, "end")
    vista.entry_apellidos_ap.insert(0, apellidos)
    try:
        vista.combo_parentesco.set("Madre")
    except Exception:
        pass


class TestGuardarEstudiante:

    def test_validacion_local_dni_corto_no_llama_controller(self, crear_vista,
                                                            usuario_admin, monkeypatch):
        vista = crear_vista(EstudianteView)
        _llenar_formulario_estudiante(vista, dni="123")

        llamadas = []
        monkeypatch.setattr(estudiante_controller, "crear_estudiante",
                            lambda data: llamadas.append(data) or (True, "ok", 1))

        vista._guardar_estudiante()
        assert llamadas == []
        assert "8 dígitos" in vista.label_form_status.cget("text")

    def test_guardar_delega_en_controller(self, crear_vista, usuario_admin, monkeypatch):
        vista = crear_vista(EstudianteView)
        _llenar_formulario_estudiante(vista)
        _llenar_apoderado(vista)

        capturadas = {}

        def fake_crear(data):
            capturadas.update(data)
            return True, "Estudiante registrado correctamente", 99

        monkeypatch.setattr(estudiante_controller, "crear_estudiante", fake_crear)
        monkeypatch.setattr(estudiante_controller, "crear_apoderado",
                            lambda data: (True, "ok", 55))
        monkeypatch.setattr(estudiante_controller, "asociar_apoderado",
                            lambda *a, **kw: (True, "ok"))
        monkeypatch.setattr(estudiante_controller, "listar_estudiantes", lambda **kw: [])
        monkeypatch.setattr(estudiante_controller, "obtener_apoderados_por_estudiante",
                            lambda id_est: [])

        vista._guardar_estudiante()

        assert capturadas.get("dni") == "12345678"
        assert capturadas.get("nombres") == "Juan"
        assert capturadas.get("apellidos") == "Perez"

    def test_error_del_controller_se_muestra(self, crear_vista, usuario_admin, monkeypatch):
        vista = crear_vista(EstudianteView)
        _llenar_formulario_estudiante(vista)
        _llenar_apoderado(vista)

        monkeypatch.setattr(estudiante_controller, "crear_estudiante",
                            lambda data: (False, "El DNI ya está registrado", None))

        vista._guardar_estudiante()
        assert "ya está registrado" in vista.label_form_status.cget("text")


class TestRegistrarPago:

    def test_sin_estudiante_muestra_error(self, crear_vista, usuario_admin):
        vista = crear_vista(PagoView)
        vista._matriculas_map = {}
        vista._cuotas_map = {}
        vista.combo_estudiante.set("")
        vista._registrar_pago()
        assert "Seleccione un estudiante" in vista.label_form_status.cget("text")

    def test_sin_cuota_muestra_error(self, crear_vista, usuario_admin):
        vista = crear_vista(PagoView)
        vista._matriculas_map = {"Alumno - Tarifa": 1}
        vista.combo_estudiante.configure(values=["Alumno - Tarifa"])
        vista.combo_estudiante.set("Alumno - Tarifa")
        vista._cuotas_map = {}
        vista._registrar_pago()
        assert "Seleccione una cuota" in vista.label_form_status.cget("text")

    def test_sin_monto_muestra_error(self, crear_vista, usuario_admin):
        vista = crear_vista(PagoView)
        vista._matriculas_map = {"Alumno - Tarifa": 1}
        vista.combo_estudiante.configure(values=["Alumno - Tarifa"])
        vista.combo_estudiante.set("Alumno - Tarifa")
        vista._cuotas_map = {"2026-08 - S/100.00 (PENDIENTE)": 7}
        vista.combo_cuota.configure(values=["2026-08 - S/100.00 (PENDIENTE)"])
        vista.combo_cuota.set("2026-08 - S/100.00 (PENDIENTE)")
        vista.entry_monto.delete(0, "end")
        vista._registrar_pago()
        assert "Ingrese el monto" in vista.label_form_status.cget("text")

    def test_pago_valido_delega_en_controller(self, crear_vista, usuario_admin, monkeypatch):
        vista = crear_vista(PagoView)
        vista._matriculas_map = {"Alumno - Tarifa": 1}
        vista.combo_estudiante.configure(values=["Alumno - Tarifa"])
        vista.combo_estudiante.set("Alumno - Tarifa")
        vista._cuotas_map = {"2026-08 - S/100.00 (PENDIENTE)": 7}
        vista.combo_cuota.configure(values=["2026-08 - S/100.00 (PENDIENTE)"])
        vista.combo_cuota.set("2026-08 - S/100.00 (PENDIENTE)")
        vista.entry_monto.delete(0, "end")
        vista.entry_monto.insert(0, "50.5")

        llamadas = []
        monkeypatch.setattr(pago_controller, "registrar_pago",
                            lambda data: llamadas.append(data) or (True, "Pago registrado", 1))
        monkeypatch.setattr(pago_controller, "listar_pagos", lambda limit=100, offset=0: [])
        monkeypatch.setattr(pago_controller, "listar_matriculas_activas", lambda: [])

        vista._registrar_pago()

        assert len(llamadas) == 1
        assert llamadas[0]["id_cuota"] == 7
        assert llamadas[0]["id_usuario"] == usuario_admin["id_usuario"]


class TestLogin:

    def test_credenciales_invalidas_muestran_error(self, crear_vista, monkeypatch):
        errores_login = []

        def on_success(usuario):
            errores_login.append(usuario)

        try:
            vista = crear_vista(LoginView, on_login_success=on_success)
        except Exception as e:
            pytest.skip(f"No se pudo instanciar LoginView: {e}")

        vista.entry_usuario.insert(0, "admin")
        vista.entry_password.insert(0, "malaclave")

        monkeypatch.setattr(login_controller, "iniciar_sesion",
                            lambda u, p: (False, "Credenciales incorrectas o usuario desactivado", None))

        vista._on_login()
        assert "incorrectas" in vista.label_error.cget("text").lower()

    def test_login_exitoso_invoca_callback_y_cierra(self, crear_vista, monkeypatch):
        resultado = []

        try:
            vista = crear_vista(LoginView,
                                on_login_success=lambda u: resultado.append(u))
        except Exception as e:
            pytest.skip(f"No se pudo instanciar LoginView: {e}")

        vista.entry_usuario.insert(0, "admin")
        vista.entry_password.insert(0, "admin123")

        usuario_falso = {"id_usuario": 1, "username": "admin", "rol": "ADMIN"}
        monkeypatch.setattr(login_controller, "iniciar_sesion",
                            lambda u, p: (True, "ok", usuario_falso))

        vista._on_login()
        assert resultado and resultado[0]["username"] == "admin"


class TestRecuperarPassword:

    @pytest.fixture
    def dialogo(self, ctk_root):
        import customtkinter as ctk
        try:
            ctk_root.update()
            dlg = RecuperarPasswordDialog(ctk_root)
            ctk_root.update()
        except Exception as e:
            pytest.skip(f"No se pudo abrir el dialogo (grab/display): {e}")
        yield dlg
        try:
            if dlg.winfo_exists():
                dlg.destroy()
        except Exception:
            pass

    def test_pin_incorrecto_rechazado(self, dialogo):
        dialogo.entry_pin.insert(0, "pin_equivocado")
        dialogo.entry_nueva.insert(0, "ClaveNueva77")
        dialogo.entry_confirmar.insert(0, "ClaveNueva77")

        dialogo._restablecer()
        assert "incorrecto" in dialogo.label_error.cget("text").lower()

    def test_passwords_distintas_rechazadas(self, dialogo):
        from utils.constants import PIN_EMERGENCIA_DEFECTO
        dialogo.entry_pin.insert(0, PIN_EMERGENCIA_DEFECTO)
        dialogo.entry_nueva.insert(0, "ClaveNueva77")
        dialogo.entry_confirmar.insert(0, "Distinta99")

        dialogo._restablecer()
        assert "no coinciden" in dialogo.label_error.cget("text")
