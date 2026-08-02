from repositories import tarifa_repository
from models.tarifa import Tarifa
from services import auditoria_service
from utils.dates import get_today
from utils.logger import logger


def crear_tarifa(data: dict) -> tuple[bool, str, int | None]:
    nombre = data.get("nombre", "")
    monto = data.get("monto", 0)
    id_categoria = data.get("id_categoria")

    if not nombre:
        return False, "El nombre es obligatorio", None
    if not id_categoria:
        return False, "La categoría es obligatoria", None
    if monto <= 0:
        return False, "El monto debe ser mayor a 0", None

    tarifa = Tarifa(
        id_categoria=id_categoria,
        nombre=nombre,
        monto=monto,
        descripcion=data.get("descripcion", ""),
        fecha_inicio=data.get("fecha_inicio", get_today()),
        fecha_fin=data.get("fecha_fin", ""),
        observaciones=data.get("observaciones", ""),
    )

    id_tarifa = tarifa_repository.insertar(tarifa)

    auditoria_service.registrar_insert(
        id_usuario=1,
        tabla="tarifa",
        id_registro=id_tarifa,
        valores_nuevos=f"nombre={nombre}, monto={monto}",
    )

    logger.info(f"Tarifa creada: {nombre} - S/{monto}")
    return True, "Tarifa creada correctamente", id_tarifa


def editar_tarifa(id_tarifa: int, data: dict) -> tuple[bool, str]:
    tarifa = tarifa_repository.obtener_por_id(id_tarifa)
    if not tarifa:
        return False, "Tarifa no encontrada"

    tarifa_obj = Tarifa(
        id_tarifa=id_tarifa,
        id_categoria=data.get("id_categoria", tarifa["id_categoria"]),
        nombre=data.get("nombre", tarifa["nombre"]),
        monto=data.get("monto", tarifa["monto"]),
        descripcion=data.get("descripcion", tarifa.get("descripcion", "")),
        fecha_inicio=data.get("fecha_inicio", tarifa["fecha_inicio"]),
        fecha_fin=data.get("fecha_fin", tarifa["fecha_fin"] or ""),
        observaciones=data.get("observaciones", tarifa.get("observaciones", "")),
        activo=tarifa["activo"],
    )
    tarifa_repository.actualizar(tarifa_obj)

    return True, "Tarifa actualizada correctamente"


def obtener_tarifa(id_tarifa: int) -> dict | None:
    return tarifa_repository.obtener_por_id(id_tarifa)


def listar_tarifas_por_categoria(id_categoria: int) -> list[dict]:
    return tarifa_repository.obtener_por_categoria(id_categoria)


def listar_tarifas_activas() -> list[dict]:
    return tarifa_repository.obtener_activas()
