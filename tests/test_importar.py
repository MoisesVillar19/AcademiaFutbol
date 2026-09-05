"""Tests del servicio de importacion CSV/Excel (validacion e import atomica)."""
from services import importar_service, estudiante_service


FILA_VALIDA = {
    "DNI": "50101010",
    "Nombres": "Import",
    "Apellidos": "Valido",
    "Fecha_Nacimiento": "2012-05-14",
    "Sexo": "M",
}


def test_fila_sin_dni_reporta_error():
    fila = {"DNI": "", "Nombres": "X", "Apellidos": "Y"}
    errores = importar_service.validar_fila(fila, 1)
    assert any("DNI" in e for e in errores)


def test_fila_sin_nombres_reporta_error():
    fila = {"DNI": "52525252", "Nombres": "", "Apellidos": "Y"}
    errores = importar_service.validar_fila(fila, 2)
    assert any("Nombres" in e for e in errores)


def test_fila_valida_sin_errores():
    errores = importar_service.validar_fila(FILA_VALIDA.copy(), 1)
    assert errores == []


def test_importar_estudiante_simple():
    filas = [FILA_VALIDA.copy()]
    exito, msg, res = importar_service.importar_estudiantes(filas)
    assert exito is True
    assert res["estudiantes_creados"] == 1
    assert res["errores"] == []

    estudiantes = estudiante_service.listar_estudiantes()
    assert any(e.get("dni") == "50101010" for e in estudiantes)


def test_importar_estudiante_con_apoderado_principal():
    fila = FILA_VALIDA.copy()
    fila.update({
        "DNI_Apoderado": "50909999",
        "Nombres_Apoderado": "Mama",
        "Apellidos_Apoderado": "Valida",
        "Parentesco": "Madre",
    })
    exito, msg, res = importar_service.importar_estudiantes([fila])
    assert exito is True
    assert res["estudiantes_creados"] == 1
    assert res["apoderados_creados"] == 1
    assert res["asociaciones_creadas"] == 1

    estudiante = next(e for e in estudiante_service.listar_estudiantes()
                      if e.get("dni") == "50101010")
    apoderados = estudiante_service.obtener_apoderados_por_estudiante(estudiante["id_estudiante"])
    principales = [a for a in apoderados if a["es_principal"]]
    assert len(principales) == 1


def test_importar_duplicado_cuenta_como_error_no_duplica():
    exito, _, _ = importar_service.importar_estudiantes([FILA_VALIDA.copy()])
    assert exito

    exito, msg, res = importar_service.importar_estudiantes([FILA_VALIDA.copy()])
    assert len(res["errores"]) == 1
    assert res["estudiantes_creados"] == 0


def test_importacion_lote_mixto_exitos_y_errores():
    fila_mala = {"DNI": "50303030", "Nombres": "", "Apellidos": ""}
    filas = [FILA_VALIDA.copy(), fila_mala]
    exito, msg, res = importar_service.importar_estudiantes(filas)
    assert res["estudiantes_creados"] == 1
    assert len(res["errores"]) == 1


def test_campos_disponibles_y_obligatorios_expuestos():
    campos = importar_service.obtener_campos_disponibles()
    assert "DNI" in campos and "DNI_Apoderado" in campos
    obligatorios = importar_service.obtener_campos_obligatorios()
    assert set(["DNI", "Nombres", "Apellidos"]).issubset(set(obligatorios))
