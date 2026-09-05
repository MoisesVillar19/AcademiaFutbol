"""Smoke tests UI: cada vista se instancia contra la BD en memoria sin errores."""
import pytest

pytestmark = pytest.mark.ui

from views.dashboard.dashboard_view import DashboardView
from views.estudiantes.estudiante_view import EstudianteView
from views.matriculas.matricula_view import MatriculaView
from views.pagos.pago_view import PagoView
from views.inventario.inventario_view import InventarioView
from views.importar.importar_view import ImportarView
from views.reportes.reporte_view import ReporteView
from views.auditoria.auditoria_view import AuditoriaView
from views.tarifas.tarifa_view import TarifaView
from views.configuracion.configuracion_view import ConfiguracionView
from views.usuarios.usuario_view import UsuarioView
from widgets.date_picker import DatePicker

VISTAS_PRINCIPALES = [
    DashboardView,
    EstudianteView,
    MatriculaView,
    PagoView,
    InventarioView,
    ImportarView,
    ReporteView,
]

VISTAS_ADMIN = [
    AuditoriaView,
    TarifaView,
    ConfiguracionView,
    UsuarioView,
]


@pytest.mark.parametrize("cls", VISTAS_PRINCIPALES)
def test_vista_accesible_para_todos_los_roles(crear_vista, usuario_admin, cls):
    vista = crear_vista(cls)
    assert vista.winfo_exists()


@pytest.mark.parametrize("cls", VISTAS_ADMIN)
def test_vista_admin_como_administrador(crear_vista, usuario_admin, cls):
    vista = crear_vista(cls)
    assert vista.winfo_exists()


@pytest.mark.parametrize("cls", VISTAS_ADMIN[:1])
def test_auditoria_denegada_para_secretaria(crear_vista, usuario_secretaria, cls):
    """SECRETARIA ve el mensaje de acceso denegado en secciones restringidas."""
    vista = crear_vista(cls)
    assert vista.winfo_exists()
    textos = []
    for hijo in vista.winfo_children():
        try:
            textos.append(hijo.cget("text"))
        except Exception:
            pass
    assert any("Acceso denegado" in str(t) for t in textos)


def test_estudiante_view_tiene_componentes_clave(crear_vista, usuario_admin):
    vista = crear_vista(EstudianteView)
    assert vista.entry_busqueda.winfo_exists()
    assert vista.entry_dni.winfo_exists()
    assert vista.entry_nombres.winfo_exists()
    assert vista.btn_guardar.winfo_exists()
    # label_status arranca vacio o con el contador inicial de la lista
    assert isinstance(vista.label_status.cget("text"), str)


def test_pago_view_tiene_componentes_clave(crear_vista, usuario_admin):
    vista = crear_vista(PagoView)
    assert vista.combo_estudiante.winfo_exists()
    assert vista.combo_cuota.winfo_exists()
    assert vista.entry_monto.winfo_exists()
    assert vista.combo_metodo.winfo_exists()


def test_date_picker_set_y_get():
    """DatePicker redondea set/get ISO (sin display propio necesario)."""
    try:
        import customtkinter as ctk
        root = ctk.CTk()
    except Exception as e:
        pytest.skip(f"Display no disponible: {e}")

    try:
        dp = DatePicker(root)
        dp.set("2020-05-10 14:30:00")
        assert dp.get() == "2020-05-10"

        dp.set("")
        assert dp.get() == ""

        dp.delete()
        assert dp.get() == ""

        dp.set("2021-11-03")
        assert dp.get() == "2021-11-03"
    finally:
        root.destroy()
