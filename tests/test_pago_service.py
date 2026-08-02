from services import pago_service, cuota_service, matricula_service
from repositories import persona_repository, estudiante_repository
from models.persona import Persona
from models.estudiante import Estudiante
from models.tarifa import Tarifa
from database.connection import fetch_one
from utils.dates import get_today


_counter = 0

def _crear_cuota_para_pago():
    """Helper: crea persona, estudiante, matrícula y cuota. Retorna id_cuota."""
    global _counter
    _counter += 1
    dni = f"660000{_counter:04d}"

    persona = Persona(
        id_persona=None, dni=dni, nombres="Pago", apellidos="Test",
        fecha_nacimiento="2000-01-01", sexo="M", direccion="", telefono="", correo=""
    )
    id_persona = persona_repository.insertar(persona)

    estudiante = Estudiante(
        id_estudiante=None, id_persona=id_persona, estado="ACTIVO",
        fecha_ingreso=get_today(), fecha_retiro=None
    )
    id_estudiante = estudiante_repository.insertar(estudiante)

    from repositories.tarifa_repository import obtener_activas, insertar as insertar_tarifa
    tarifas = obtener_activas()
    if tarifas:
        id_tarifa = tarifas[0]["id_tarifa"]
    else:
        cat = fetch_one("SELECT id_categoria FROM categoria LIMIT 1")
        if not cat:
            return None
        tarifa = Tarifa(
            id_categoria=cat["id_categoria"],
            nombre="Tarifa Test",
            monto=300.0,
            fecha_inicio=get_today(),
        )
        id_tarifa = insertar_tarifa(tarifa)

    exito, msg, id_matricula = matricula_service.crear_matricula({
        "id_estudiante": id_estudiante,
        "id_tarifa": id_tarifa,
        "monto_pactado": 300.0,
        "dia_vencimiento": 15,
    })
    if not id_matricula:
        return None

    id_cuota = cuota_service.crear_cuota(
        id_matricula=id_matricula,
        monto_total=300.0,
        fecha_vencimiento="2026-12-15",
        periodo="2026-12"
    )
    return id_cuota


def test_registrar_pago():
    id_cuota = _crear_cuota_para_pago()
    assert id_cuota is not None

    exito, msg, id_pago = pago_service.registrar_pago({
        "id_usuario": 1,
        "id_cuota": id_cuota,
        "monto_pagado": 150.0,
        "metodo_pago": "EFECTIVO",
        "observacion": "Pago parcial test",
    })
    assert exito is True
    assert id_pago is not None
    assert id_pago > 0


def test_registrar_pago_monto_excede():
    id_cuota = _crear_cuota_para_pago()
    assert id_cuota is not None

    exito, msg, id_pago = pago_service.registrar_pago({
        "id_usuario": 1,
        "id_cuota": id_cuota,
        "monto_pagado": 500.0,
        "metodo_pago": "EFECTIVO",
    })
    assert exito is False


def test_registrar_pago_cuota_no_existe():
    exito, msg, id_pago = pago_service.registrar_pago({
        "id_usuario": 1,
        "id_cuota": 99999,
        "monto_pagado": 50.0,
        "metodo_pago": "EFECTIVO",
    })
    assert exito is False


def test_registrar_pago_metodo_invalido():
    id_cuota = _crear_cuota_para_pago()
    assert id_cuota is not None

    exito, msg, id_pago = pago_service.registrar_pago({
        "id_usuario": 1,
        "id_cuota": id_cuota,
        "monto_pagado": 50.0,
        "metodo_pago": "BITCOIN",
    })
    assert exito is False


def test_registrar_pago_monto_cero():
    id_cuota = _crear_cuota_para_pago()
    assert id_cuota is not None

    exito, msg, id_pago = pago_service.registrar_pago({
        "id_usuario": 1,
        "id_cuota": id_cuota,
        "monto_pagado": 0,
        "metodo_pago": "EFECTIVO",
    })
    assert exito is False


def test_listar_pagos():
    pagos = pago_service.listar_pagos()
    assert isinstance(pagos, list)


def test_obtener_pago_no_existe():
    pago = pago_service.obtener_pago(99999)
    assert pago is None
