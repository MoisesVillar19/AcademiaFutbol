from services import categoria_service


def crear_categoria(data: dict) -> tuple[bool, str, int | None]:
    return categoria_service.crear_categoria(data)


def editar_categoria(id_categoria: int, data: dict) -> tuple[bool, str]:
    return categoria_service.editar_categoria(id_categoria, data)


def desactivar_categoria(id_categoria: int) -> tuple[bool, str]:
    return categoria_service.desactivar_categoria(id_categoria)


def listar_categorias() -> list[dict]:
    return categoria_service.listar_categorias()


def listar_todas() -> list[dict]:
    return categoria_service.listar_todas_las_categorias()


def obtener_categoria(id_categoria: int) -> dict | None:
    return categoria_service.obtener_categoria(id_categoria)
