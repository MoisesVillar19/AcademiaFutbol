from services import estudiante_service


def test_crear_estudiante():
    exito, msg, id_est = estudiante_service.crear_estudiante({
        "dni": "99999999",
        "nombres": "Carlos",
        "apellidos": "Tester",
        "sexo": "M",
    })
    assert exito is True
    assert id_est is not None
    assert id_est > 0


def test_crear_estudiante_duplicado():
    estudiante_service.crear_estudiante({
        "dni": "88888888",
        "nombres": "Dup",
        "apellidos": "Test",
        "sexo": "M",
    })
    exito, msg, id_est = estudiante_service.crear_estudiante({
        "dni": "88888888",
        "nombres": "Dup2",
        "apellidos": "Test2",
        "sexo": "M",
    })
    assert exito is False


def test_crear_estudiante_sin_dni():
    exito, msg, id_est = estudiante_service.crear_estudiante({
        "nombres": "NoDni",
        "apellidos": "Test",
        "sexo": "M",
    })
    assert exito is False


def test_editar_estudiante():
    exito, msg, id_est = estudiante_service.crear_estudiante({
        "dni": "76543210",
        "nombres": "Edit",
        "apellidos": "Test",
        "sexo": "M",
    })
    assert exito is True

    exito, msg = estudiante_service.editar_estudiante(id_est, {
        "nombres": "Editado",
        "apellidos": "Modificado",
        "dni": "76543210",
        "sexo": "M",
    })
    assert exito is True

    est = estudiante_service.obtener_estudiante(id_est)
    assert est["nombres"] == "Editado"
    assert est["apellidos"] == "Modificado"


def test_editar_estudiante_no_existe():
    exito, msg = estudiante_service.editar_estudiante(99999, {
        "nombres": "X",
        "apellidos": "Y",
        "dni": "12345678",
        "sexo": "M",
    })
    assert exito is False


def test_listar_estudiantes():
    estudiante_service.crear_estudiante({
        "dni": "11111111",
        "nombres": "List",
        "apellidos": "Test",
        "sexo": "M",
    })
    estudiantes = estudiante_service.listar_estudiantes()
    assert isinstance(estudiantes, list)
    assert len(estudiantes) >= 1


def test_obtener_estudiante():
    exito, msg, id_est = estudiante_service.crear_estudiante({
        "dni": "22222222",
        "nombres": "Get",
        "apellidos": "Test",
        "sexo": "M",
    })
    est = estudiante_service.obtener_estudiante(id_est)
    assert est is not None
    assert est["id_estudiante"] == id_est


def test_obtener_estudiante_no_existe():
    est = estudiante_service.obtener_estudiante(99999)
    assert est is None
