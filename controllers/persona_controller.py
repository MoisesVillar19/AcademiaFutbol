from services import persona_service, auth_service
from utils.validators import validate_documento, validate_not_empty, validate_sex, validate_email


def _get_id_usuario() -> int:
    return auth_service.id_usuario_sesion()


def crear_persona(data: dict) -> tuple[bool, str, int | None]:
    dni = data.get("dni", "")
    tipo_doc = data.get("tipo_documento", "DNI")
    if not dni:
        return False, "El documento es obligatorio", None
    if not validate_documento(dni, tipo_doc):
        if tipo_doc == "CARNET":
            return False, "El Carnet debe tener 9 dígitos", None
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

    correo = data.get("correo", "")
    if correo and not validate_email(correo):
        return False, "Correo no válido", None

    return persona_service.crear_persona(data, id_usuario=_get_id_usuario())


def editar_persona(id_persona: int, data: dict) -> tuple[bool, str]:
    dni = data.get("dni", "")
    tipo_doc = data.get("tipo_documento", "DNI")
    if dni and not validate_documento(dni, tipo_doc):
        if tipo_doc == "CARNET":
            return False, "El Carnet debe tener 9 dígitos"
        return False, "El DNI debe tener 8 dígitos"

    sexo = data.get("sexo", "")
    if sexo and not validate_sex(sexo):
        return False, "Sexo debe ser M o F"

    correo = data.get("correo", "")
    if correo and not validate_email(correo):
        return False, "Correo no válido"

    return persona_service.editar_persona(id_persona, data, id_usuario=_get_id_usuario())


def buscar_por_dni(dni: str) -> dict | None:
    return persona_service.buscar_por_dni(dni)


def obtener_persona(id_persona: int) -> dict | None:
    return persona_service.obtener_persona(id_persona)


def listar_personas(activo: int | None = None) -> list[dict]:
    return persona_service.listar_personas(activo=activo)
