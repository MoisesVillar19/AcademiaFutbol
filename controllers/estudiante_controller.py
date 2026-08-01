from services import estudiante_service, apoderado_service
from utils.validators import (validate_dni, validate_not_empty, validate_sex,
                               validate_estado_estudiante)


def crear_estudiante(data: dict) -> tuple[bool, str, int | None]:
    dni = data.get("dni", "")
    if not dni:
        return False, "El DNI es obligatorio", None
    if not validate_dni(dni):
        return False, "El DNI debe tener 8 dígitos", None

    nombres = data.get("nombres", "")
    error = validate_not_empty(nombres, "Nombres")
    if error:
        return False, error, None

    apellidos = data.get("apellidos", "")
    error = validate_not_empty(apellidos, "Apellidos")
    if error:
        return False, error, None

    sexo = data.get("sexo", "")
    if sexo and not validate_sex(sexo):
        return False, "Sexo debe ser M o F", None

    return estudiante_service.crear_estudiante(data)


def editar_estudiante(id_estudiante: int, data: dict) -> tuple[bool, str]:
    dni = data.get("dni", "")
    if dni and not validate_dni(dni):
        return False, "El DNI debe tener 8 dígitos"

    sexo = data.get("sexo", "")
    if sexo and not validate_sex(sexo):
        return False, "Sexo debe ser M o F"

    return estudiante_service.editar_estudiante(id_estudiante, data)


def registrar_retiro(id_estudiante: int) -> tuple[bool, str]:
    return estudiante_service.registrar_retiro(id_estudiante)


def registrar_reingreso(id_estudiante: int) -> tuple[bool, str]:
    return estudiante_service.registrar_reingreso(id_estudiante)


def asociar_apoderado(id_estudiante: int, id_apoderado: int,
                      es_principal: bool = False) -> tuple[bool, str]:
    return estudiante_service.asociar_apoderado(id_estudiante, id_apoderado, es_principal)


def desasociar_apoderado(id_estudiante: int, id_apoderado: int) -> tuple[bool, str]:
    return estudiante_service.desasociar_apoderado(id_estudiante, id_apoderado)


def listar_estudiantes(activo: int | None = None) -> list[dict]:
    return estudiante_service.listar_estudiantes(activo=activo)


def obtener_estudiante(id_estudiante: int) -> dict | None:
    return estudiante_service.obtener_estudiante(id_estudiante)


def obtener_apoderados_por_estudiante(id_estudiante: int) -> list[dict]:
    return estudiante_service.obtener_apoderados_por_estudiante(id_estudiante)


def crear_apoderado(data: dict) -> tuple[bool, str, int | None]:
    dni = data.get("dni", "")
    if not dni:
        return False, "El DNI es obligatorio", None
    if not validate_dni(dni):
        return False, "El DNI debe tener 8 dígitos", None

    parentesco = data.get("parentesco", "")
    error = validate_not_empty(parentesco, "Parentesco")
    if error:
        return False, error, None

    return apoderado_service.crear_apoderado(data)


def listar_apoderados(activo: int | None = None) -> list[dict]:
    return apoderado_service.listar_apoderados(activo=activo)


def obtener_apoderado(id_apoderado: int) -> dict | None:
    return apoderado_service.obtener_apoderado(id_apoderado)
