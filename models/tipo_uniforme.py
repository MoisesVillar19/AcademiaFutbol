from dataclasses import dataclass


@dataclass
class TipoUniforme:
    id_tipo_uniforme: int | None = None
    nombre: str = ""
    descripcion: str = ""
    activo: int = 1
