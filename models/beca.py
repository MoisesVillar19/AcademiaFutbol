from dataclasses import dataclass


@dataclass
class Beca:
    id_beca: int | None = None
    nombre: str = ""
    tipo: str = ""
    valor: float = 0.0
    observacion: str = ""
    activo: int = 1
