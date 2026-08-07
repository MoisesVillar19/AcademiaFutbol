from dataclasses import dataclass


@dataclass
class Tarifa:
    id_tarifa: int | None = None
    id_categoria: int = 0
    nombre: str = ""
    monto: float = 0.0
    descripcion: str = ""
    observaciones: str = ""
    activo: int = 1
