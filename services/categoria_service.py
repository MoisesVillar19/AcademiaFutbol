from repositories import categoria_repository
from services import auditoria_service
from utils.logger import logger


def crear_categoria(data: dict) -> tuple[bool, str, int | None]:
    nombre = data.get("nombre", "").strip()
    edad_min = data.get("edad_min")
    edad_max = data.get("edad_max")

    if not nombre:
        return False, "El nombre es obligatorio", None
    if edad_min is None or edad_max is None:
        return False, "Las edades son obligatorias", None
    try:
        edad_min = int(edad_min)
        edad_max = int(edad_max)
    except (ValueError, TypeError):
        return False, "Las edades deben ser números", None
    if edad_min < 0 or edad_max < 0:
        return False, "Las edades no pueden ser negativas", None
    if edad_min > edad_max:
        return False, "La edad mínima no puede ser mayor que la máxima", None

    if categoria_repository.existe_nombre(nombre):
        return False, "Ya existe una categoría con ese nombre", None

    id_categoria = categoria_repository.insertar(nombre, edad_min, edad_max)

    auditoria_service.registrar_insert(
        id_usuario=1,
        tabla="categoria",
        id_registro=id_categoria,
        valores_nuevos=f"nombre={nombre}, edad_min={edad_min}, edad_max={edad_max}",
    )

    logger.info(f"Categoría creada: {nombre} ({edad_min}-{edad_max})")
    return True, "Categoría creada correctamente", id_categoria


def editar_categoria(id_categoria: int, data: dict) -> tuple[bool, str]:
    cat = categoria_repository.obtener_por_id(id_categoria)
    if not cat:
        return False, "Categoría no encontrada"

    nombre = data.get("nombre", cat["nombre"]).strip()
    edad_min = data.get("edad_min", cat["edad_min"])
    edad_max = data.get("edad_max", cat["edad_max"])

    try:
        edad_min = int(edad_min)
        edad_max = int(edad_max)
    except (ValueError, TypeError):
        return False, "Las edades deben ser números"

    if edad_min > edad_max:
        return False, "La edad mínima no puede ser mayor que la máxima"

    if categoria_repository.existe_nombre(nombre, exclude_id=id_categoria):
        return False, "Ya existe otra categoría con ese nombre"

    categoria_repository.actualizar(id_categoria, nombre, edad_min, edad_max)
    return True, "Categoría actualizada correctamente"


def desactivar_categoria(id_categoria: int) -> tuple[bool, str]:
    cat = categoria_repository.obtener_por_id(id_categoria)
    if not cat:
        return False, "Categoría no encontrada"
    categoria_repository.soft_delete(id_categoria)
    return True, "Categoría desactivada correctamente"


def listar_categorias() -> list[dict]:
    return categoria_repository.obtener_activas()


def listar_todas_las_categorias() -> list[dict]:
    return categoria_repository.obtener_todas()


def obtener_categoria(id_categoria: int) -> dict | None:
    return categoria_repository.obtener_por_id(id_categoria)
