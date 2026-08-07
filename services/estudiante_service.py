from repositories import estudiante_repository, persona_repository, estudiante_apoderado_repository
from models.estudiante import Estudiante
from models.persona import Persona
from services import auditoria_service
from utils.dates import get_today
from utils.logger import logger


def crear_estudiante(data: dict, id_usuario: int = 1) -> tuple[bool, str, int | None]:
    dni = data.get("dni", "")

    if not dni:
        return False, "El DNI es obligatorio", None

    persona = persona_repository.obtener_por_dni(dni)
    if persona:
        id_persona = persona["id_persona"]
        existente = estudiante_repository.obtener_por_persona(id_persona)
        if existente:
            return False, "Esta persona ya es estudiante", None
    else:
        nombres = data.get("nombres", "")
        apellidos = data.get("apellidos", "")
        if not nombres or not apellidos:
            return False, "Nombres y apellidos son obligatorios para nueva persona", None

        persona_obj = Persona(
            dni=dni,
            tipo_documento=data.get("tipo_documento", "DNI"),
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=data.get("fecha_nacimiento", ""),
            sexo=data.get("sexo", ""),
            direccion=data.get("direccion", ""),
            telefono=data.get("telefono", ""),
            correo=data.get("correo", ""),
        )
        id_persona = persona_repository.insertar(persona_obj)

    estudiante = Estudiante(
        id_persona=id_persona,
        estado="ACTIVO",
        fecha_ingreso=get_today(),
    )
    id_estudiante = estudiante_repository.insertar(estudiante)

    auditoria_service.registrar_insert(
        id_usuario=id_usuario,
        tabla="estudiante",
        id_registro=id_estudiante,
        valores_nuevos=f"dni={dni}, estado=ACTIVO",
    )

    logger.info(f"Estudiante creado: DNI={dni}")
    return True, "Estudiante registrado correctamente", id_estudiante


def editar_estudiante(id_estudiante: int, data: dict) -> tuple[bool, str]:
    estudiante = estudiante_repository.obtener_por_id(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado"

    persona = persona_repository.obtener_por_id(estudiante["id_persona"])
    if persona:
        dni = data.get("dni", persona["dni"])
        if persona_repository.existe_dni(dni, exclude_id=estudiante["id_persona"]):
            return False, "El DNI ya está registrado por otra persona"

        persona_obj = Persona(
            id_persona=estudiante["id_persona"],
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

    return True, "Estudiante actualizado correctamente"


def registrar_retiro(id_estudiante: int, id_usuario: int = 1) -> tuple[bool, str]:
    estudiante = estudiante_repository.obtener_por_id(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado"

    if estudiante["estado"] == "RETIRADO":
        return False, "El estudiante ya está retirado"

    estudiante_repository.cambiar_estado(id_estudiante, "RETIRADO", get_today())

    auditoria_service.registrar_update(
        id_usuario=id_usuario,
        tabla="estudiante",
        id_registro=id_estudiante,
        valores_anteriores=f"estado={estudiante['estado']}",
        valores_nuevos="estado=RETIRADO",
    )

    logger.info(f"Estudiante retirado: ID={id_estudiante}")
    return True, "Retiro registrado correctamente"


def registrar_reingreso(id_estudiante: int, id_usuario: int = 1) -> tuple[bool, str]:
    estudiante = estudiante_repository.obtener_por_id(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado"

    if estudiante["estado"] != "RETIRADO":
        return False, "Solo pueden reingresar estudiantes retirados"

    estudiante_repository.cambiar_estado(id_estudiante, "REINGRESANTE")

    auditoria_service.registrar_update(
        id_usuario=id_usuario,
        tabla="estudiante",
        id_registro=id_estudiante,
        valores_anteriores=f"estado=RETIRADO",
        valores_nuevos="estado=REINGRESANTE",
    )

    logger.info(f"Estudiante reingreso: ID={id_estudiante}")
    return True, "Reingreso registrado correctamente"


def asociar_apoderado(id_estudiante: int, id_apoderado: int,
                      es_principal: bool = False) -> tuple[bool, str]:
    if estudiante_apoderado_repository.existe_relacion(id_estudiante, id_apoderado):
        return False, "Este apoderado ya está asociado al estudiante"

    if es_principal:
        estudiante_apoderado_repository.marcar_principal(id_estudiante, id_apoderado)

    estudiante_apoderado_repository.insertar(
        id_estudiante=id_estudiante,
        id_apoderado=id_apoderado,
        es_principal=1 if es_principal else 0,
    )

    return True, "Apoderado asociado correctamente"


def desasociar_apoderado(id_estudiante: int, id_apoderado: int) -> tuple[bool, str]:
    apoderados = estudiante_apoderado_repository.obtener_por_estudiante(id_estudiante)
    for ap in apoderados:
        if ap["id_apoderado"] == id_apoderado and ap["es_principal"]:
            return False, "No se puede desasociar el apoderado principal"

    estudiante_apoderado_repository.eliminar(id_estudiante, id_apoderado)
    return True, "Apoderado desasociado correctamente"


def listar_estudiantes(activo: int | None = None, estado: str | None = None) -> list[dict]:
    return estudiante_repository.obtener_todos(activo=activo, estado=estado)


def obtener_estudiante(id_estudiante: int) -> dict | None:
    return estudiante_repository.obtener_por_id_con_persona(id_estudiante)


def obtener_apoderados_por_estudiante(id_estudiante: int) -> list[dict]:
    return estudiante_apoderado_repository.obtener_por_estudiante(id_estudiante)


def tiene_apoderado_principal(id_estudiante: int) -> bool:
    return estudiante_apoderado_repository.tiene_principal(id_estudiante)
