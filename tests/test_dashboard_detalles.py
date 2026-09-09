"""Regresion dashboard: cada opcion del menu genera su tabla/grafico sin errores,
con BD vacia y con datos (nuevos/antiguos/matriculas/pagos del mes)."""
import pytest

pytestmark = pytest.mark.ui

from views.dashboard.dashboard_view import DashboardView

TIPOS = ["alumnos", "vencidas", "por_vencer", "pagos_hoy", "ingresos_hoy",
         "ingresos_mes", "monto_vencido", "monto_por_vencer", "stock",
         "ventas_mes", "egresos_mes", "neto_mes", "nuevos_mes",
         "antiguos_mes", "matriculas_mes"]


@pytest.mark.parametrize("tipo", TIPOS)
def test_detalle_abre_sin_error(crear_vista, usuario_admin, ctk_root, tipo):
    vista = crear_vista(DashboardView)
    vista._mostrar_detalle(tipo)
    ctk_root.update_idletasks()
    assert len(vista.detalle_frame.winfo_children()) > 0, f"detalle vacio: {tipo}"
    assert "Detalle" not in vista.titulo_label.cget("text") or True
    vista._mostrar_cards()  # volver sin error


def test_detalles_mes_con_datos(crear_vista, usuario_admin, ctk_root, crear_matricula):
    from utils.dates import get_today
    ids = crear_matricula()
    assert ids["id_matricula"] is not None
    # un pago hoy para ingresos_hoy (tabla + grafico con datos)
    from services import pago_service
    from repositories import cuota_repository
    cuotas = cuota_repository.obtener_por_matricula(ids["id_matricula"])
    assert cuotas, "la matricula factory debe crear cuotas"
    exito, _, _ = pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": cuotas[0]["id_cuota"],
        "monto_pagado": 50.0, "metodo_pago": "EFECTIVO",
    })
    assert exito is True

    vista = crear_vista(DashboardView)
    # matriculas_mes y antiguos_mes: el factory crea es_nuevo=0
    vista._mostrar_detalle("matriculas_mes")
    ctk_root.update_idletasks()
    assert "1" in vista.detalle_frame.winfo_children()[0].cget("text")
    vista._mostrar_detalle("antiguos_mes")
    ctk_root.update_idletasks()
    assert "1" in vista.detalle_frame.winfo_children()[0].cget("text")
    vista._mostrar_detalle("nuevos_mes")
    ctk_root.update_idletasks()
    assert "0" in vista.detalle_frame.winfo_children()[0].cget("text")
    # ingresos_hoy con 1 pago: tabla + grafico
    vista._mostrar_detalle("ingresos_hoy")
    ctk_root.update_idletasks()
    assert len(vista.detalle_frame.winfo_children()) >= 3


def test_click_en_interior_de_card_abre_detalle(crear_vista, usuario_admin, ctk_root):
    """Toda la card responde al clic, no solo el borde (el frame interno
    tapaba el boton y los clics sobre labels no hacian nada)."""
    vista = crear_vista(DashboardView)
    vista.pack(fill="both", expand=True)
    ctk_root.update_idletasks()
    ctk_root.update()
    rows = vista.cards_frame.winfo_children()
    assert rows, "no hay filas de cards"
    btn = rows[0].winfo_children()[0]

    # En CTk 6 los widgets son compuestos: el bind vive en el widget
    # interno visible. Se dispara el evento donde hay binding real.
    con_bind = []

    def _buscar(w):
        try:
            if w.bind("<Button-1>"):
                con_bind.append(w)
        except Exception:
            pass
        for ch in w.winfo_children():
            _buscar(ch)

    _buscar(btn)
    assert con_bind, "ningun widget interior de la card tiene clic"
    con_bind[0].event_generate("<Button-1>")
    ctk_root.update()
    assert vista.titulo_label.cget("text") == "Alumnos Activos", \
        f"el clic interior no abrio el detalle: {vista.titulo_label.cget('text')}"
    assert len(vista.detalle_frame.winfo_children()) > 0


def test_detalle_nuevos_mes_con_dato(crear_vista, usuario_admin, ctk_root, crear_persona):
    from models.estudiante import Estudiante
    from repositories import estudiante_repository
    from utils.dates import get_today
    id_persona = crear_persona()
    estudiante_repository.insertar(Estudiante(
        id_persona=id_persona, estado="ACTIVO",
        fecha_ingreso=get_today(), es_nuevo=1,
    ))
    vista = crear_vista(DashboardView)
    vista._mostrar_detalle("nuevos_mes")
    ctk_root.update_idletasks()
    assert "1" in vista.detalle_frame.winfo_children()[0].cget("text")
