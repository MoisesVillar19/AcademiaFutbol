from repositories import tipo_uniforme_repository
from models.tipo_uniforme import TipoUniforme
from services import auditoria_service
from utils.logger import logger
from utils.validators import validate_not_empty


def crear_tipo_uniforme(data: dict) -> tuple[bool, str, int | None]:
    nombre = data.get("nombre", "").strip()
    err = validate_not_empty(nombre, "Nombre")
    if err:
        return False, err, None
    if tipo_uniforme_repository.obtener_por_nombre(nombre):
        return False, "Ya existe un tipo de uniforme con ese nombre", None
    tipo = TipoUniforme(nombre=nombre, descripcion=data.get("descripcion", ""))
    id_tipo = tipo_uniforme_repository.insertar(tipo)
    auditoria_service.registrar_insert(auditoria_service.id_usuario_sesion(), "tipo_uniforme", id_tipo, f"nombre={nombre}")
    logger.info(f"Tipo uniforme creado: {nombre}")
    return True, "Tipo de uniforme creado correctamente", id_tipo


def listar_tipos(activo: int | None = 1) -> list[dict]:
    return tipo_uniforme_repository.obtener_todos(activo=activo)


def desactivar_tipo(id_tipo: int) -> tuple[bool, str]:
    t = tipo_uniforme_repository.obtener_por_id(id_tipo)
    if not t:
        return False, "Tipo no encontrado"
    if t["activo"] == 0:
        return False, "Ya está desactivado"
    tipo_uniforme_repository.soft_delete(id_tipo)
    auditoria_service.registrar_desactivacion(auditoria_service.id_usuario_sesion(), "tipo_uniforme", id_tipo, "activo=1", "activo=0")
    return True, "Tipo desactivado correctamente"
