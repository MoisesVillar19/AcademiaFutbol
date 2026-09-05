"""Tests del servicio de actualizacion (comparacion de versiones y throttling)."""
from datetime import datetime, timedelta
import pytest

from updater import update_service


def test_comparar_versiones_mayor_menor_igual():
    assert update_service.comparar_versiones("1.0.0", "1.0.1") == -1
    assert update_service.comparar_versiones("1.0.2", "1.0.1") == 1
    assert update_service.comparar_versiones("1.0.0", "1.0.0") == 0
    assert update_service.comparar_versiones("2.0.0", "1.9.9") == 1
    assert update_service.comparar_versiones("1.0", "1.0.0") == -1


@pytest.mark.parametrize("estado,esperado", [
    ({}, True),
    ({"ultima_verificacion": None}, True),
])
def test_debe_verificar_sin_estado_previo(monkeypatch, estado, esperado):
    monkeypatch.setattr(update_service, "_cargar_estado", lambda: estado)
    assert update_service.debe_verificar() is esperado


def test_debe_verificar_false_dentro_de_ventana(monkeypatch):
    reciente = (datetime.now() - timedelta(hours=1)).isoformat()
    monkeypatch.setattr(update_service, "_cargar_estado",
                        lambda: {"ultima_verificacion": reciente})
    assert update_service.debe_verificar() is False


def test_debe_verificar_true_pasada_la_ventana(monkeypatch):
    antigua = (datetime.now() - timedelta(hours=72)).isoformat()
    monkeypatch.setattr(update_service, "_cargar_estado",
                        lambda: {"ultima_verificacion": antigua})
    assert update_service.debe_verificar() is True


def test_debe_verificar_con_fecha_corrupta(monkeypatch):
    monkeypatch.setattr(update_service, "_cargar_estado",
                        lambda: {"ultima_verificacion": "no-es-fecha"})
    assert update_service.debe_verificar() is True


def test_registrar_rechazo_y_verificacion_persisten(monkeypatch, tmp_path):
    state_file = tmp_path / "state.json"
    monkeypatch.setattr(update_service, "_STATE_DIR", str(tmp_path))
    monkeypatch.setattr(update_service, "_STATE_FILE", str(state_file))

    update_service.registrar_verificacion()
    estado = update_service._cargar_estado()
    assert "ultima_verificacion" in estado

    update_service.registrar_rechazo("9.9.9")
    estado = update_service._cargar_estado()
    assert estado["rechazado_version"] == "9.9.9"
