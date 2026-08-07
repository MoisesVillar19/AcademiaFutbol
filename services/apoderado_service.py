from repositories import apoderado_repository, persona_repository, estudiante_apoderado_repository
from models.apoderado import Apoderado
from models.persona import Persona
from services import auditoria_service
from utils.logger import logger


def crear_apoderado(data: dict, id_usuario: int = 1) -> tuple[bool, str, int | None]:
    dni = data.get("dni", "")
    parentesco = data.get("parentesco", "")

    if not dni:
        return False, "El DNI es obligatorio", None
    if not parentesco:
        return False, "El parentesco es obligatorio", None

    persona = persona_repository.obtener_por_dni(dni)
    if persona:
        id_persona = persona["id_persona"]
        if apoderado_repository.obtener_por_persona(id_persona):
            return False, "Esta persona ya es apoderado", None
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

    apoderado = Apoderado(
        id_persona=id_persona,
        parentesco=parentesco,
        ocupacion=data.get("ocupacion", ""),
        telefono=data.get("telefono", ""),
        direccion=data.get("direccion", ""),
    )
    id_apoderado = apoderado_repository.insertar(apoderado)

    auditoria_service.registrar_insert(
        id_usuario=id_usuario,
        tabla="apoderado",
        id_registro=id_apoderado,
        valores_nuevos=f"dni={dni}, parentesco={parentesco}",
    )

    logger.info(f"Apoderado creado: DNI={dni}")
    return True, "Apoderado registrado correctamente", id_apoderado


def editar_apoderado(id_apoderado: int, data: dict) -> tuple[bool, str]:
    apoderado = apoderado_repository.obtener_por_id(id_apoderado)
    if not apoderado:
        return False, "Apoderado no encontrado"

    from repositories import persona_repository
    from models.persona import Persona

    persona_actual = persona_repository.obtener_por_id(apoderado["id_persona"])
    if persona_actual:
        persona_obj = Persona(
            id_persona=apoderado["id_persona"],
            dni=data.get("dni", persona_actual["dni"]),
            tipo_documento=data.get("tipo_documento", persona_actual.get("tipo_documento", "DNI")),
            nombres=data.get("nombres", persona_actual["nombres"]),
            apellidos=data.get("apellidos", persona_actual["apellidos"]),
            fecha_nacimiento=persona_actual.get("fecha_nacimiento", ""),
            sexo=persona_actual.get("sexo", ""),
            telefono=data.get("telefono", persona_actual.get("telefono", "")),
            direccion=data.get("direccion", persona_actual.get("direccion", "")),
            correo=persona_actual.get("correo", ""),
        )
        persona_repository.actualizar(persona_obj)

    parentesco = data.get("parentesco", apoderado["parentesco"])

    apoderado_obj = Apoderado(
        id_apoderado=id_apoderado,
        id_persona=apoderado["id_persona"],
        parentesco=parentesco,
        ocupacion=data.get("ocupacion", apoderado["occupacion"] if apoderado.get("occupacion") else apoderado.get("ocupacion", "")),
        activo=apoderado["activo"],
    )
    apoderado_repository.actualizar(apoderado_obj)

    logger.info(f"Apoderado actualizado: id={id_apoderado}")
    return True, "Apoderado actualizado correctamente"


def asociar_a_estudiante(id_estudiante: int, id_apoderado: int,
                         es_principal: bool = False, id_usuario: int = 1) -> tuple[bool, str]:
    if estudiante_apoderado_repository.existe_relacion(id_estudiante, id_apoderado):
        return False, "Este apoderado ya está asociado al estudiante"

    if es_principal:
        estudiante_apoderado_repository.marcar_principal(id_estudiante, id_apoderado)

    estudiante_apoderado_repository.insertar(
        id_estudiante=id_estudiante,
        id_apoderado=id_apoderado,
        es_principal=1 if es_principal else 0,
    )

    auditoria_service.registrar_insert(
        id_usuario=id_usuario,
        tabla="estudiante_apoderado",
        id_registro=id_estudiante,
        valores_nuevos=f"id_estudiante={id_estudiante}, id_apoderado={id_apoderado}, principal={es_principal}",
    )

    return True, "Apoderado asociado correctamente"


def desasociar_de_estudiante(id_estudiante: int, id_apoderado: int) -> tuple[bool, str]:
    if estudiante_apoderado_repository.tiene_principal(id_estudiante):
        apoderados = estudiante_apoderado_repository.obtener_por_estudiante(id_estudiante)
        for ap in apoderados:
            if ap["id_apoderado"] == id_apoderado and ap["es_principal"]:
                return False, "No se puede desasociar el apoderado principal"

    estudiante_apoderado_repository.eliminar(id_estudiante, id_apoderado)
    return True, "Apoderado desasociado correctamente"


def listar_apoderados(activo: int | None = None) -> list[dict]:
    return apoderado_repository.obtener_todos(activo=activo)


def obtener_apoderado(id_apoderado: int) -> dict | None:
    return apoderado_repository.obtener_por_id_con_persona(id_apoderado)


def obtener_apoderados_por_estudiante(id_estudiante: int) -> list[dict]:
    return estudiante_apoderado_repository.obtener_por_estudiante(id_estudiante)
