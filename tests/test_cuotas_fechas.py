"""Tests de generacion de cuotas: fechas validas y periodos duplicados."""
from services import cuota_service
from repositories import cuota_repository


def test_fecha_vencimiento_ajusta_dia_31_a_febrero(crear_matricula):
    ids = crear_matricula(dia_vencimiento=31)

    # La primera cuota se genera para el mes actual con dia 31 (o el ultimo dia del mes)
    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    anio, mes = int(cuota["periodo"][:4]), int(cuota["periodo"][5:7])
    import calendar
    ultimo_dia = calendar.monthrange(anio, mes)[1]

    fecha = cuota["fecha_vencimiento"]
    assert int(fecha[8:10]) == min(31, ultimo_dia)


def test_generar_siguiente_cuota_feb_con_dia_30(obtener_tarifa, crear_estudiante):
    from services import matricula_service
    id_tarifa, _ = obtener_tarifa(monto=100.0)
    id_est = crear_estudiante()
    _, _, id_mat = matricula_service.crear_matricula({
        "id_estudiante": id_est, "id_tarifa": id_tarifa,
        "monto_pactado": 100.0, "dia_vencimiento": 30,
    })

    # Forzar periodo enero y generar febrero: dia 30 -> 28/29
    from database.connection import execute_query
    execute_query(
        "UPDATE cuota SET periodo = '2027-01', fecha_vencimiento = '2027-01-30' WHERE id_cuota = ?",
        ((cuota_repository.obtener_por_matricula(id_mat)[0]["id_cuota"]),),
    )

    exito, msg, id_nueva = cuota_service.generar_siguiente_cuota(id_mat, 100.0, 30)
    assert exito, msg

    nueva = cuota_repository.obtener_por_id(id_nueva)
    assert nueva["periodo"] == "2027-02"
    assert nueva["fecha_vencimiento"] in ("2027-02-28", "2027-02-29")


def test_no_duplica_periodo_existente(crear_matricula):
    """El guardia debe impedir generar un periodo que ya existe para la matricula."""
    from database.connection import execute_query
    ids = crear_matricula()

    # Forzar la cuota existente a '2030-05' e insertar una fila futura '2030-06'
    # con fecha de orden anterior, de modo que la ultima cuota sea 2030-05.
    execute_query(
        "UPDATE cuota SET periodo = '2030-05', fecha_vencimiento = '2030-05-15' WHERE id_cuota = ?",
        (ids["id_cuota"],),
    )
    execute_query(
        """INSERT INTO cuota (id_matricula, periodo, fecha_vencimiento,
                              monto_total, saldo, estado)
           VALUES (?, '2030-06', '2030-01-01', 0, 0, 'PAGADO')""",
        (ids["id_matricula"],),
    )

    exito, msg, id_nueva = cuota_service.generar_siguiente_cuota(ids["id_matricula"], 200.0, 15)
    assert exito is False
    assert "2030-06" in msg


def test_actualizar_pago_conserva_monto_mora(usuario_admin, crear_matricula):
    ids = crear_matricula(monto_pactado=100.0)
    from models.cuota import Cuota
    from database.connection import transaccion

    with transaccion():
        pass
    cuota_repository.actualizar(Cuota(
        id_cuota=ids["id_cuota"],
        id_matricula=ids["id_matricula"],
        periodo="2020-01",
        fecha_vencimiento="2020-01-15",
        monto_total=110.0,
        monto_mora=10.0,
        saldo=110.0,
        estado="VENCIDO",
    ))

    exito, msg = cuota_service.actualizar_pago(ids["id_cuota"], 60.0)
    assert exito is True

    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["monto_mora"] == 10.0
    assert cuota["monto_pagado"] == 60.0
    assert cuota["saldo"] == 50.0
    assert cuota["estado"] == "PARCIAL"


def test_crear_cuota_estado_inicial_pendiente(crear_matricula):
    ids = crear_matricula()
    cuota = cuota_repository.obtener_por_id(ids["id_cuota"])
    assert cuota["estado"] == "PENDIENTE"
    assert cuota["monto_pagado"] == 0
    assert cuota["saldo"] == cuota["monto_total"]
