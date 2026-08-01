from dataclasses import dataclass


@dataclass
class CategoriaProducto:
    id_categoria_producto: int | None = None
    nombre: str = ""
    activo: int = 1
