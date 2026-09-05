"""Tests adicionales del servicio de pagos: multiples pagos, fechas e ingresos."""
from services import pago_service, cuota_service
from repositories import cuota_repository, detalle_pago_repository


def test_multiples_pagos_parciales_hasta_pagado(crear_matricula):
    ids = crear_matricula(monto_pactado=300.0)
    id_cuota = ids["id_cuota"]

    for monto in (100.0, 100.0, 100.0):
        exito, msg, id_pago = pago_service.registrar_pago({
            "id_usuario": 1, "id_cuota": id_cuota,
            "monto_pagado": monto, "metodo_pago": "YAPE",
        })
        assert exito, msg

    cuota = cuota_repository.obtener_por_id(id_cuota)
    assert cuota["estado"] == "PAGADO"
    assert cuota["saldo"] == 0
    assert cuota["monto_pagado"] == 300.0


def test_pago_cuota_ya_pagada_rechazado(crear_matricula):
    ids = crear_matricula(monto_pactado=100.0)
    pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": ids["id_cuota"],
        "monto_pagado": 100.0, "metodo_pago": "EFECTIVO",
    })
    exito, msg, _ = pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": ids["id_cuota"],
        "monto_pagado": 10.0, "metodo_pago": "EFECTIVO",
    })
    assert exito is False
    assert "pagada" in msg.lower()


def test_detalles_por_pago(crear_matricula):
    ids = crear_matricula(monto_pactado=120.0)
    exito, _, id_pago = pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": ids["id_cuota"],
        "monto_pagado": 40.0, "metodo_pago": "PLIN",
    })
    detalles = detalle_pago_repository.obtener_por_pago(id_pago)
    assert len(detalles) == 1
    assert detalles[0]["monto_pagado"] == 40.0
    assert detalles[0]["id_cuota"] == ids["id_cuota"]


def test_listar_por_fecha_e_ingresos(crear_matricula):
    from utils.dates import get_today
    hoy = get_today()

    ids = crear_matricula(monto_pactado=80.0)
    pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": ids["id_cuota"],
        "monto_pagado": 30.0, "metodo_pago": "EFECTIVO",
    })
    pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": ids["id_cuota"],
        "monto_pagado": 20.0, "metodo_pago": "TRANSFERENCIA",
    })

    pagos = pago_service.listar_por_fecha(hoy, hoy)
    montos = [p["monto_total"] for p in pagos]
    assert 30.0 in montos and 20.0 in montos

    ingresos = pago_service.obtener_ingresos_por_fecha(hoy, hoy)
    assert ingresos >= 50.0

    cantidad = pago_service.contar_pagos_por_fecha(hoy, hoy)
    assert cantidad >= 2


def test_recibos_unicos_en_rapida_sucesion(crear_matricula):
    ids = crear_matricula(monto_pactado=90.0)
    recibos = set()
    for _ in range(3):
        exito, _, id_pago = pago_service.registrar_pago({
            "id_usuario": 1, "id_cuota": ids["id_cuota"],
            "monto_pagado": 30.0, "metodo_pago": "EFECTIVO",
        })
        assert exito
        recibos.add(pago_service.obtener_pago(id_pago)["numero_recibo"])
    assert len(recibos) == 3


def test_listar_por_estudiante(crear_matricula):
    ids = crear_matricula(monto_pactado=60.0)
    pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": ids["id_cuota"],
        "monto_pagado": 20.0, "metodo_pago": "EFECTIVO",
    })
    pagos = pago_service.listar_por_estudiante(ids["id_estudiante"])
    assert isinstance(pagos, list)
