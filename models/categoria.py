from dataclasses import dataclass


@dataclass
class Categoria:
    id_categoria: int | None = None
    nombre: str = ""
    edad_min: int = 0
    edad_max: int = 0
    activo: int = 1
