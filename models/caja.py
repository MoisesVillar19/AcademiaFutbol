from dataclasses import dataclass


@dataclass
class Caja:
    id_caja: int | None = None
    id_almacen: int = 0
    nombre: str = ""
    responsable: str = ""
    activo: int = 1
