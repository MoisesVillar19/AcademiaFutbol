"""Tests de atomicidad transaccional (context manager transaccion)."""
import pytest
from services import pago_service, matricula_service
from repositories import cuota_repository, pago_repository, matricula_repository


def test_pago_atomico_rollback_si_falla_detalle(crear_matricula, monkeypatch):
    """Si falla el detalle_pago, ni el pago ni la cuota deben quedar modificados."""
    ids = crear_matricula(monto_pactado=200.0)

    from repositories import detalle_pago_repository
    def _boom(*a, **kw):
        raise RuntimeError("fallo simulado en detalle")
    monkeypatch.setattr(detalle_pago_repository, "insertar", _boom)

    with pytest.raises(RuntimeError):
        pago_service.registrar_pago({
            "id_usuario": 1,
            "id_cuota": ids["id_cuota"],
            "monto_pagado": 50.0,
            "metodo_pago": "EFECTIVO",
        })

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["monto_pagado"] == 0
    assert cuota["estado"] == "PENDIENTE"
    pagos = pago_repository.obtener_todos(limit=100)
    assert len(pagos) == 0


def test_matricula_atomica_si_falla_cuota(obtener_tarifa, crear_estudiante, monkeypatch):
    """Si falla la generacion de la primera cuota, la matricula no debe crearse."""
    id_tarifa, _ = obtener_tarifa()
    id_est = crear_estudiante()

    def _boom(*a, **kw):
        raise RuntimeError("fallo simulado al generar cuota")
    monkeypatch.setattr(matricula_service.cuota_service, "generar_siguiente_cuota", _boom)

    with pytest.raises(RuntimeError):
        matricula_service.crear_matricula({
            "id_estudiante": id_est, "id_tarifa": id_tarifa, "monto_pactado": 150.0,
        })

    mats = matricula_repository.obtener_por_estudiante(id_est)
    assert len(mats) == 0


def test_transaccion_commit_normal(crear_matricula):
    """Sanity: fuera de rollback, las escrituras dentro de transaccion persisten."""
    ids = crear_matricula(monto_pactado=200.0)
    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota is not None
    assert cuota["monto_total"] == 200.0


def test_importacion_fila_revertida_completa(monkeypatch):
    """Si la asociacion apoderado falla, el estudiante de esa fila no debe quedar."""
    from services import importar_service, estudiante_service
    from repositories import estudiante_apoderado_repository

    filas = [{
        "DNI": "44555666",
        "Nombres": "Importado",
        "Apellidos": "Atomico",
        "DNI_Apoderado": "44555999",
        "Nombres_Apoderado": "Apo",
        "Apellidos_Apoderado": "Atomico",
        "Parentesco": "Padre",
    }]

    def _boom(*a, **kw):
        raise RuntimeError("fallo simulado en asociacion")
    monkeypatch.setattr(estudiante_apoderado_repository, "insertar", _boom)

    exito, msg, res = importar_service.importar_estudiantes(filas)
    assert res["errores"], "la fila debio reportar error"

    persona = estudiante_service.listar_estudiantes(activo=None)
    dnis = [e.get("dni") for e in persona]
    assert "44555666" not in dnis, "el estudiante debio revertirse con su fila"
