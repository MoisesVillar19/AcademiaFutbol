"""DatePicker escribible + indicador de carga."""
import pytest

pytestmark = pytest.mark.ui

from widgets.date_picker import DatePicker, parsear_fecha


@pytest.mark.parametrize("entrada,esperado", [
    ("2026-09-06", "2026-09-06"),
    ("06/09/2026", "2026-09-06"),
    ("06-09-2026", "2026-09-06"),
    ("06.09.2026", "2026-09-06"),
    ("06092026", "2026-09-06"),
    ("20260906", "2026-09-06"),
    (" 2026-09-06 ", "2026-09-06"),
    ("2026-02-30", None),   # fecha imposible
    ("32/01/2026", None),
    ("13/13/2026", None),
    ("", None),
    (None, None),
    ("abc", None),
    ("2026-13-01", None),
    ("1899-01-01", None),   # fuera de rango
])
def test_parsear_fecha(entrada, esperado):
    assert parsear_fecha(entrada) == esperado


def test_picker_escribir_y_normalizar(crear_vista):
    vista = crear_vista(DatePicker)
    vista.entry_fecha.insert(0, "06/09/2026")
    vista._on_normalizar()
    assert vista.get() == "2026-09-06"
    assert vista.entry_fecha.get() == "2026-09-06"


def test_picker_invalido_marca_rojo_y_get_vacio(crear_vista):
    from widgets import date_picker as dp
    vista = crear_vista(DatePicker)
    vista.entry_fecha.insert(0, "99/99/9999")
    vista._on_normalizar()
    assert vista.get() == ""
    assert vista.entry_fecha.cget("border_color") == dp.BORDE_MAL


def test_picker_set_delete(crear_vista):
    vista = crear_vista(DatePicker)
    vista.set("2026-01-15")
    assert vista.get() == "2026-01-15"
    vista.delete()
    assert vista.get() == ""


def test_mostrar_cargando_ciclo(crear_vista, ctk_root):
    from utils.ui_helpers import mostrar_cargando
    vista = crear_vista(DatePicker)
    detener = mostrar_cargando(vista, "Probando")
    ctk_root.update_idletasks()
    detener()
    ctk_root.update_idletasks()
    # no quedan labels de carga flotantes
    textos = []

    def _rec(w):
        try:
            t = w.cget("text")
            if t:
                textos.append(str(t))
        except Exception:
            pass
        for ch in w.winfo_children():
            _rec(ch)

    _rec(vista)
    assert not any("Probando" in t for t in textos)
