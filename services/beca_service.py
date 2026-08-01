from repositories import beca_repository
from models.beca import Beca
from services import auditoria_service
from utils.logger import logger


def crear_beca(data: dict) -> tuple[bool, str, int | None]:
    nombre = data.get("nombre", "")
    tipo = data.get("tipo", "")
    valor = data.get("valor", 0)

    if not nombre:
        return False, "El nombre es obligatorio", None
    if not tipo:
        return False, "El tipo es obligatorio", None
    if tipo not in ("PORCENTAJE", "MONTO_FIJO"):
        return False, "Tipo no válido. Use PORCENTAJE o MONTO_FIJO", None
    if valor <= 0:
        return False, "El valor debe ser mayor a 0", None

    beca = Beca(
        nombre=nombre,
        tipo=tipo,
        valor=valor,
        observacion=data.get("observacion", ""),
    )

    id_beca = beca_repository.insertar(beca)

    auditoria_service.registrar_insert(
        id_usuario=1,
        tabla="beca",
        id_registro=id_beca,
        valores_nuevos=f"nombre={nombre}, tipo={tipo}, valor={valor}",
    )

    logger.info(f"Beca creada: {nombre} ({tipo} {valor})")
    return True, "Beca creada correctamente", id_beca


def editar_beca(id_beca: int, data: dict) -> tuple[bool, str]:
    beca = beca_repository.obtener_por_id(id_beca)
    if not beca:
        return False, "Beca no encontrada"

    beca_obj = Beca(
        id_beca=id_beca,
        nombre=data.get("nombre", beca["nombre"]),
        tipo=data.get("tipo", beca["tipo"]),
        valor=data.get("valor", beca["valor"]),
        observacion=data.get("observacion", beca["observacion"] or ""),
        activo=beca["activo"],
    )
    beca_repository.actualizar(beca_obj)

    return True, "Beca actualizada correctamente"


def obtener_beca(id_beca: int) -> dict | None:
    return beca_repository.obtener_por_id(id_beca)


def listar_becas(activo: int | None = None) -> list[dict]:
    return beca_repository.obtener_todas(activo=activo)
