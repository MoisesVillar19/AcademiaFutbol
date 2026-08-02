from repositories import persona_repository
from models.persona import Persona
from services import auditoria_service
from utils.logger import logger


def crear_persona(data: dict, id_usuario: int = 1) -> tuple[bool, str, int | None]:
    dni = data.get("dni", "")
    nombres = data.get("nombres", "")
    apellidos = data.get("apellidos", "")

    if not dni:
        return False, "El DNI es obligatorio", None
    if not nombres:
        return False, "Los nombres son obligatorios", None
    if not apellidos:
        return False, "Los apellidos son obligatorios", None

    if persona_repository.existe_dni(dni):
        return False, "El DNI ya está registrado", None

    persona = Persona(
        dni=dni,
        nombres=nombres,
        apellidos=apellidos,
        fecha_nacimiento=data.get("fecha_nacimiento", ""),
        sexo=data.get("sexo", ""),
        direccion=data.get("direccion", ""),
        telefono=data.get("telefono", ""),
        correo=data.get("correo", ""),
    )

    id_persona = persona_repository.insertar(persona)

    auditoria_service.registrar_insert(
        id_usuario=id_usuario,
        tabla="persona",
        id_registro=id_persona,
        valores_nuevos=f"dni={dni}, nombres={nombres}, apellidos={apellidos}",
    )

    logger.info(f"Persona creada: DNI={dni}")
    return True, "Persona registrada correctamente", id_persona


def editar_persona(id_persona: int, data: dict, id_usuario: int = 1) -> tuple[bool, str]:
    persona = persona_repository.obtener_por_id(id_persona)
    if not persona:
        return False, "Persona no encontrada"

    dni = data.get("dni", persona["dni"])
    if persona_repository.existe_dni(dni, exclude_id=id_persona):
        return False, "El DNI ya está registrado por otra persona"

    persona_obj = Persona(
        id_persona=id_persona,
        dni=dni,
        nombres=data.get("nombres", persona["nombres"]),
        apellidos=data.get("apellidos", persona["apellidos"]),
        fecha_nacimiento=data.get("fecha_nacimiento", persona["fecha_nacimiento"] or ""),
        sexo=data.get("sexo", persona["sexo"] or ""),
        direccion=data.get("direccion", persona["direccion"] or ""),
        telefono=data.get("telefono", persona["telefono"] or ""),
        correo=data.get("correo", persona["correo"] or ""),
        activo=persona["activo"],
    )
    persona_repository.actualizar(persona_obj)

    auditoria_service.registrar_update(
        id_usuario=id_usuario,
        tabla="persona",
        id_registro=id_persona,
        valores_anteriores=f"dni={persona['dni']}",
        valores_nuevos=f"dni={dni}",
    )

    return True, "Persona actualizada correctamente"


def buscar_por_dni(dni: str) -> dict | None:
    return persona_repository.obtener_por_dni(dni)


def obtener_persona(id_persona: int) -> dict | None:
    return persona_repository.obtener_por_id(id_persona)


def listar_personas(activo: int | None = None) -> list[dict]:
    return persona_repository.obtener_todos(activo=activo)
