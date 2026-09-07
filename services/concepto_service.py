from repositories import concepto_cobro_repository, concepto_item_repository
from services import auditoria_service
from utils.logger import logger

TIPOS_VALIDOS = ("INSCRIPCION", "MENSUALIDAD", "REINGRESO", "PROMOCION", "CAMPEONATO", "OTRO")


def listar_conceptos(activo: int | None = 1) -> list[dict]:
    return concepto_cobro_repository.obtener_todos(activo=activo)


def obtener_concepto(id_concepto: int) -> dict | None:
    return concepto_cobro_repository.obtener_por_id(id_concepto)


def obtener_items(id_concepto: int) -> list[dict]:
    return concepto_item_repository.obtener_por_concepto(id_concepto)


def crear_concepto(data: dict, id_usuario: int | None = None) -> tuple[bool, str, int | None]:
    nombre = (data.get("nombre") or "").strip()
    tipo = (data.get("tipo") or "").strip()
    try:
        monto = float(data.get("monto", 0))
    except Exception:
        return False, "Monto inválido", None
    if not nombre:
        return False, "El nombre es obligatorio", None
    if tipo not in TIPOS_VALIDOS:
        return False, f"Tipo no válido: {tipo}", None
    if monto < 0:
        return False, "El monto no puede ser negativo", None
    if concepto_cobro_repository.obtener_todos(activo=None):
        for c in concepto_cobro_repository.obtener_todos(activo=None):
            if c["nombre"].lower() == nombre.lower():
                return False, "Ya existe un concepto con ese nombre", None
    try:
        id_concepto = concepto_cobro_repository.insertar({"nombre": nombre, "tipo": tipo, "monto": monto, "descripcion": data.get("descripcion", ""), "activo": 1})
        items = data.get("items", [])
        if items:
            concepto_item_repository.reemplazar_items(id_concepto, items)
        auditoria_service.registrar_insert(id_usuario or auditoria_service.id_usuario_sesion_or_system(), "concepto_cobro", id_concepto, f"nombre={nombre}, tipo={tipo}, monto={monto}")
        logger.info(f"Concepto creado: {nombre} {monto}")
        return True, "Concepto creado correctamente", id_concepto
    except Exception as e:
        logger.error(f"Error crear concepto: {e}")
        return False, str(e), None


def editar_concepto(id_concepto: int, data: dict) -> tuple[bool, str]:
    c = concepto_cobro_repository.obtener_por_id(id_concepto)
    if not c:
        return False, "Concepto no encontrado"
    nombre = (data.get("nombre") or c["nombre"]).strip()
    tipo = (data.get("tipo") or c["tipo"]).strip()
    try:
        monto = float(data.get("monto", c["monto"]))
    except Exception:
        return False, "Monto inválido", None
    if tipo not in TIPOS_VALIDOS:
        return False, f"Tipo no válido: {tipo}", None
    concepto_cobro_repository.actualizar(id_concepto, {"nombre": nombre, "tipo": tipo, "monto": monto, "descripcion": data.get("descripcion", c.get("descripcion", ""))})
    if "items" in data:
        concepto_item_repository.reemplazar_items(id_concepto, data["items"])
    auditoria_service.registrar_update(auditoria_service.id_usuario_sesion_or_system(), "concepto_cobro", id_concepto, f"nombre={c['nombre']}", f"nombre={nombre}, monto={monto}")
    return True, "Concepto actualizado"


def desactivar_concepto(id_concepto: int) -> tuple[bool, str]:
    c = concepto_cobro_repository.obtener_por_id(id_concepto)
    if not c:
        return False, "Concepto no encontrado"
    concepto_cobro_repository.soft_delete(id_concepto)
    auditoria_service.registrar_desactivacion(auditoria_service.id_usuario_sesion_or_system(), "concepto_cobro", id_concepto, "activo=1", "activo=0")
    return True, "Concepto desactivado"
