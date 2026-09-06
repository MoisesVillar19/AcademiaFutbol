from dataclasses import dataclass


@dataclass
class Proveedor:
    id_proveedor: int | None = None
    nombre: str = ""
    telefono: str = ""
    activo: int = 1
