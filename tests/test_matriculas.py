from services import matricula_service, cuota_service, estudiante_service
from repositories import persona_repository
from models.persona import Persona
from models.tarifa import Tarifa
from database.connection import fetch_one
from utils.dates import get_today

_counter = 0


def _crear_datos_base():
    """Helper: crea persona + estudiante + tarifa. Retorna (id_estudiante, id_tarifa)."""
    global _counter
    _counter += 1
    dni = f"550000{_counter:04d}"

    persona = Persona(
        id_persona=None, dni=dni, nombres="Matricula", apellidos="Test",
        fecha_nacimiento="2010-05-15", sexo="M", direccion="", telefono="", correo=""
    )
    id_persona = persona_repository.insertar(persona)

    exito, msg, id_estudiante = estudiante_service.crear_estudiante({
        "dni": dni, "nombres": "Matricula", "apellidos": "Test", "sexo": "M",
    })
    assert exito is True

    from repositories.tarifa_repository import obtener_activas, insertar as insertar_tarifa
    tarifas = obtener_activas()
    if tarifas:
        id_tarifa = tarifas[0]["id_tarifa"]
    else:
        cat = fetch_one("SELECT id_categoria FROM categoria LIMIT 1")
        tarifa = Tarifa(
            id_categoria=cat["id_categoria"], nombre="Tarifa Int",
            monto=150.0,
        )
        id_tarifa = insertar_tarifa(tarifa)

    return id_estudiante, id_tarifa


def test_crear_matricula():
    id_est, id_tar = _crear_datos_base()
    exito, msg, id_mat = matricula_service.crear_matricula({
        "id_estudiante": id_est,
        "id_tarifa": id_tar,
        "monto_pactado": 150.0,
        "dia_vencimiento": 10,
    })
    assert exito is True
    assert id_mat is not None
    assert id_mat > 0


def test_matricula_con_cuota_generada():
    id_est, id_tar = _crear_datos_base()
    exito, msg, id_mat = matricula_service.crear_matricula({
        "id_estudiante": id_est,
        "id_tarifa": id_tar,
        "monto_pactado": 150.0,
        "dia_vencimiento": 10,
    })
    assert exito is True

    cuotas = cuota_service.obtener_cuotas_por_matricula(id_mat)
    assert len(cuotas) >= 1
    assert cuotas[0]["monto_total"] == 150.0
    assert cuotas[0]["estado"] == "PENDIENTE"


def test_matricula_estudiante_ya_activo():
    id_est, id_tar = _crear_datos_base()
    matricula_service.crear_matricula({
        "id_estudiante": id_est, "id_tarifa": id_tar,
        "monto_pactado": 150.0, "dia_vencimiento": 10,
    })
    exito, msg, id_mat = matricula_service.crear_matricula({
        "id_estudiante": id_est, "id_tarifa": id_tar,
        "monto_pactado": 150.0, "dia_vencimiento": 10,
    })
    assert exito is False


def test_matricula_estudiante_no_existe():
    from repositories.tarifa_repository import obtener_activas
    tarifas = obtener_activas()
    if not tarifas:
        return
    exito, msg, id_mat = matricula_service.crear_matricula({
        "id_estudiante": 99999, "id_tarifa": tarifas[0]["id_tarifa"],
        "monto_pactado": 150.0, "dia_vencimiento": 10,
    })
    assert exito is False


def test_listar_matriculas_activas():
    matriculas = matricula_service.listar_matriculas_activas()
    assert isinstance(matriculas, list)


def test_obtener_matricula_por_estudiante():
    id_est, id_tar = _crear_datos_base()
    matricula_service.crear_matricula({
        "id_estudiante": id_est, "id_tarifa": id_tar,
        "monto_pactado": 150.0, "dia_vencimiento": 10,
    })
    matriculas = matricula_service.obtener_por_estudiante(id_est)
    assert isinstance(matriculas, list)
    assert len(matriculas) >= 1
