"""Tests de mora y transicion a VENCIDO (RN-020)."""
from services import cuota_service, configuracion_service
from repositories import cuota_repository


def _activar_mora(**kwargs):
    data = {"mora_habilitada": 1}
    data.update(kwargs)
    exito, _ = configuracion_service.actualizar_configuracion(data)
    assert exito


def _forzar_vencimiento(ids, fecha="2020-01-15", monto_total=200.0):
    from models.cuota import Cuota
    cuota_repository.actualizar(Cuota(
        id_cuota=ids["id_cuota"],
        id_matricula=ids["id_matricula"],
        periodo=fecha[:7],
        fecha_vencimiento=fecha,
        monto_total=monto_total,
        saldo=monto_total,
        estado="PENDIENTE",
    ))


def test_mora_deshabilitada_marca_vencido_sin_mora(crear_matricula):
    ids = crear_matricula()
    _forzar_vencimiento(ids)

    actualizadas = cuota_service.actualizar_estados_vencidos()
    assert actualizadas >= 1

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["estado"] == "VENCIDO"
    assert cuota["monto_mora"] == 0
    # Invariante: saldo = total - pagado
    assert cuota["saldo"] == cuota["monto_total"] - cuota["monto_pagado"]


def test_mora_porcentaje_aplica_y_mantiene_invariante(crear_matricula):
    _activar_mora(porcentaje_mora=10)
    ids = crear_matricula(monto_pactado=100.0)
    _forzar_vencimiento(ids, monto_total=100.0)

    cuota_service.actualizar_estados_vencidos()

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["estado"] == "VENCIDO"
    assert cuota["monto_mora"] == 10.0
    # La mora se suma tambien al monto_total para mantener la invariante
    assert cuota["monto_total"] == 110.0
    assert cuota["saldo"] == 110.0
    assert cuota["saldo"] == round(cuota["monto_total"] - cuota["monto_pagado"], 2)


def test_mora_monto_fijo(crear_matricula):
    _activar_mora(tipo_mora="MONTO_FIJO", monto_mora=25.0)
    ids = crear_matricula(monto_pactado=100.0)
    _forzar_vencimiento(ids, monto_total=100.0)

    cuota_service.actualizar_estados_vencidos()

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["monto_mora"] == 25.0
    assert cuota["monto_total"] == 125.0
    assert cuota["saldo"] == 125.0


def test_mora_no_reaplica_en_segunda_pasada(crear_matricula):
    _activar_mora(porcentaje_mora=10)
    ids = crear_matricula(monto_pactado=100.0)
    _forzar_vencimiento(ids, monto_total=100.0)

    cuota_service.actualizar_estados_vencidos()
    cuota_service.actualizar_estados_vencidos()
    cuota_service.actualizar_estados_vencidos()

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["monto_mora"] == 10.0
    assert cuota["monto_total"] == 110.0


def test_cuota_al_dia_no_se_marca_vencida(crear_matricula):
    ids = crear_matricula()
    _forzar_vencimiento(ids, fecha="2099-12-31")
    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["estado"] == "PENDIENTE"

    cuota_service.actualizar_estados_vencidos()

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["estado"] in ("PENDIENTE", "PARCIAL")
    assert cuota["monto_mora"] == 0


def test_cuota_pagada_excluida_de_proceso(crear_matricula):
    ids = crear_matricula()
    cuota_service.actualizar_pago(ids["id_cuota"], 200.0)

    antes = cuota_repository.obtener_por_id(ids["id_cuota"])
    cuota_service.actualizar_estados_vencidos()
    despues = cuota_repository.obtener_por_id(ids["id_cuota"])

    assert despues["estado"] == "PAGADO"
    assert despues["monto_total"] == antes["monto_total"]
    assert despues["saldo"] == 0


def test_pago_sobre_cuota_con_mora_respeta_nuevo_saldo(crear_matricula):
    """Tras aplicar mora, un pago parcial debe respetar el saldo inflado."""
    from services import pago_service
    _activar_mora(porcentaje_mora=10)
    ids = crear_matricula(monto_pactado=100.0)
    _forzar_vencimiento(ids, monto_total=100.0)
    cuota_service.actualizar_estados_vencidos()

    exito, msg, id_pago = pago_service.registrar_pago({
        "id_usuario": 1,
        "id_cuota": ids["id_cuota"],
        "monto_pagado": 110.0,
        "metodo_pago": "EFECTIVO",
    })
    assert exito is True

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["monto_pagado"] == 110.0
    assert cuota["saldo"] == 0
    assert cuota["estado"] == "PAGADO"


def test_mora_genera_registro_auditoria(usuario_admin, crear_matricula):
    from services import auditoria_service
    _activar_mora(porcentaje_mora=5)
    ids = crear_matricula(monto_pactado=200.0)
    _forzar_vencimiento(ids, monto_total=200.0)

    cuota_service.actualizar_estados_vencidos()

    logs = auditoria_service.obtener_logs_por_tabla("cuota")
    assert any("mora" in (l.get("valor_nuevo") or "") for l in logs)
