from dataclasses import dataclass


@dataclass
class Almacen:
    id_almacen: int | None = None
    nombre: str = ""
    direccion: str = ""
    activo: int = 1
