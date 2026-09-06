from dataclasses import dataclass


@dataclass
class Talla:
    id_talla: int | None = None
    codigo: str = ""
    descripcion: str = ""
    activo: int = 1
