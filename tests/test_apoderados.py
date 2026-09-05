"""Tests del servicio de apoderados: CRUD, principal unico y edicion (regresion)."""
from services import apoderado_service
from repositories import apoderado_repository, estudiante_apoderado_repository


def _data_apoderado(dni, **overrides):
    data = {
        "dni": dni,
        "nombres": "Apoderado",
        "apellidos": "Test",
        "parentesco": "Padre",
        "ocupacion": "Ingeniero",
        "telefono": "999888777",
        "direccion": "Av. Siempre Viva 123",
    }
    data.update(overrides)
    return data


def test_crear_apoderado_con_persona_nueva(crear_persona):
    exito, msg, id_apoderado = apoderado_service.crear_apoderado(_data_apoderado("87654321"))
    assert exito is True, msg
    assert id_apoderado > 0

    ap = apoderado_repository.obtener_por_id(id_apoderado)
    assert ap["parentesco"] == "Padre"
    assert ap["telefono"] == "999888777"


def test_crear_apoderado_reutiliza_persona_existente_por_dni(crear_persona):
    id_persona = crear_persona(dni="11112222", telefono="955555555")
    exito, msg, id_apo = apoderado_service.crear_apoderado(
        _data_apoderado("11112222", parentesco="Madre", nombres="Otro", apellidos="Nombre")
    )
    assert exito is True

    ap = apoderado_repository.obtener_por_id(id_apo)
    assert ap["id_persona"] == id_persona


def test_dni_duplicado_como_apoderado_rechazado():
    apoderado_service.crear_apoderado(_data_apoderado("33334444"))
    exito, msg, _ = apoderado_service.crear_apoderado(_data_apoderado("33334444"))
    assert exito is False
    assert "ya es apoderado" in msg.lower()


def test_editar_apoderado_persiste_telefono_y_direccion():
    """Regression: editar_apoderado descartaba telefono/direccion (bug occupacion)."""
    _, _, id_apo = apoderado_service.crear_apoderado(_data_apoderado("44445555"))

    exito, msg = apoderado_service.editar_apoderado(id_apo, {
        "telefono": "911222333",
        "direccion": "Nueva Direccion 456",
        "ocupacion": "Doctor",
    })
    assert exito is True, msg

    ap = apoderado_repository.obtener_por_id(id_apo)
    assert ap["telefono"] == "911222333"
    assert ap["direccion"] == "Nueva Direccion 456"
    assert ap["ocupacion"] == "Doctor"


def test_asociar_principal_unico(crear_estudiante):
    id_est = crear_estudiante()
    _, _, apo1 = apoderado_service.crear_apoderado(_data_apoderado("55556666"))
    _, _, apo2 = apoderado_service.crear_apoderado(_data_apoderado("66667777"))

    exito, _ = apoderado_service.asociar_a_estudiante(id_est, apo1, es_principal=True)
    assert exito

    exito, _ = apoderado_service.asociar_a_estudiante(id_est, apo2, es_principal=True)
    assert exito

    relaciones = estudiante_apoderado_repository.obtener_por_estudiante(id_est)
    principales = [r for r in relaciones if r["es_principal"]]
    assert len(principales) == 1
    assert principales[0]["id_apoderado"] == apo2


def test_no_desasociar_apoderado_principal(crear_estudiante):
    id_est = crear_estudiante()
    _, _, apo = apoderado_service.crear_apoderado(_data_apoderado("77778888"))
    apoderado_service.asociar_a_estudiante(id_est, apo, es_principal=True)

    exito, msg = apoderado_service.desasociar_de_estudiante(id_est, apo)
    assert exito is False
    assert "principal" in msg.lower()


def test_desasociar_apoderado_secundario(crear_estudiante):
    id_est = crear_estudiante()
    _, _, apo_p = apoderado_service.crear_apoderado(_data_apoderado("88889999"))
    _, _, apo_s = apoderado_service.crear_apoderado(_data_apoderado("99990000"))

    apoderado_service.asociar_a_estudiante(id_est, apo_p, es_principal=True)
    apoderado_service.asociar_a_estudiante(id_est, apo_s, es_principal=False)

    exito, msg = apoderado_service.desasociar_de_estudiante(id_est, apo_s)
    assert exito is True, msg

    ids_asociados = [r["id_apoderado"]
                     for r in estudiante_apoderado_repository.obtener_por_estudiante(id_est)]
    assert apo_s not in ids_asociados


def test_asociacion_duplicada_rechazada(crear_estudiante):
    id_est = crear_estudiante()
    _, _, apo = apoderado_service.crear_apoderado(_data_apoderado("10101010"))
    apoderado_service.asociar_a_estudiante(id_est, apo)

    exito, msg = apoderado_service.asociar_a_estudiante(id_est, apo)
    assert exito is False
    assert "ya está asociado" in msg.lower()


def test_desasociar_registra_auditoria(usuario_admin, crear_estudiante):
    from services import auditoria_service
    id_est = crear_estudiante()
    _, _, apo_p = apoderado_service.crear_apoderado(_data_apoderado("12121212"))
    _, _, apo_s = apoderado_service.crear_apoderado(_data_apoderado("13131313"))
    apoderado_service.asociar_a_estudiante(id_est, apo_p, es_principal=True)
    apoderado_service.asociar_a_estudiante(id_est, apo_s)
    apoderado_service.desasociar_de_estudiante(id_est, apo_s)

    logs = auditoria_service.obtener_logs_por_tabla("estudiante_apoderado")
    assert any(l["accion"] == "DESACTIVACION" for l in logs)
